from mkdocs.plugins import BasePlugin
from mkdocs.config import base, config_options as c
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import Files, File
from mkdocs.structure.pages import Page
from mkdocs.structure.nav import Navigation
from mkdocs.utils import normalize_url
from mkdocs.utils.templates import TemplateContext
from jinja2 import Environment, pass_context
from pathlib import PurePosixPath
from urllib.parse import urlsplit, urlunsplit
from rdflib import Graph, URIRef
from rdflib.resource import Resource
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from jinja_rdf import get_context, register_filters
from jinja_rdf.graph_handling import GraphToFilesystemHelper, TemplateSelectionHelper
from jinja_rdf.rdf_resource import RDFResource
from loguru import logger


@pass_context
def iri_resolver(context: TemplateContext, value: str | URIRef | Resource) -> str:
    """A Template filter to resolve an iri and return a normalized URL."""
    if page := context.get("config").plugins.get("mkrdf").resolve(value):
        url = page.url
    else:
        if isinstance(value, Resource):
            url = value.identifier
        else:
            url = value

    return normalize_url(str(url), page=context["page"], base=context["base_url"])


class _MkRDFPluginConfig_Selection(base.Config):
    preset = c.Optional(c.Choice(("subject_relative", "subject_all", "none")))
    query = c.Optional(c.Type(str))
    queries = c.Optional(c.ListOfItems(c.Type(str)))
    list = c.Optional(c.ListOfItems(c.URL()))
    file = c.Optional(c.File(exists=True))
    files = c.Optional(c.ListOfItems(c.File(exists=True)))


class MkRDFPluginConfig(base.Config):
    graph_file = c.Optional(c.File(exists=True))
    sparql_endpoint = c.Optional(c.URL())
    base_iri = c.Optional(c.URL())
    selection = c.SubConfig(_MkRDFPluginConfig_Selection, validate=True)
    default_template = c.Optional(c.Type(str))
    class_template_map = c.DictOfItems(
        c.Type(str), default={}
    )  # keys are always strings, while we expect IRIs here
    instance_template_map = c.DictOfItems(
        c.Type(str), default={}
    )  # keys are always strings, while we expect IRIs here


class MkRDFPlugin(BasePlugin[MkRDFPluginConfig]):
    """This is the mkrdf plugin."""

    """The resource_to_page dict is required since there is no backward relation from resource to a page."""
    resource_iri_to_page = {}

    def resolve(self, value: str | URIRef | Resource) -> Page | None:
        """A Template filter to resolve an iri and return a normalized URL."""
        if isinstance(value, Resource):
            value = value.identifier
        if isinstance(value, str):
            value = URIRef(value)
        return self.resource_iri_to_page.get(value)

    def on_files(self, files: Files, config: MkDocsConfig, **kwargs) -> Files | None:
        """For each resourceIri that results from the selection query, a File
        object is generated and registered."""

        if self.config.graph_file:
            g = Graph()
            g.parse(source=self.config.graph_file)
        elif self.config.sparql_endpoint:
            store = SPARQLStore(query_endpoint=self.config.sparql_endpoint)
            g = Graph(store=store)
        self.graph = g

        gtfh = GraphToFilesystemHelper(self.config.base_iri)
        nodes = set(gtfh.selection_to_nodes(self.config.selection, g))

        for resource_iri, path, _ in gtfh.nodes_to_paths(nodes):
            logger.debug(f'Append file for iri: "{resource_iri}" at path: "{path}"')
            file = File.generated(config=config, src_uri=path + ".md", content="")
            file.resource_iri = resource_iri
            files.append(file)
        return files

    def on_page_content(self, html, page, config, files):
        logger.debug(f"page meta: {page.meta}")
        if "title" not in page.meta:
            # insert some title
            pass

        # register resource IRIs
        if "resource_iri" in page.meta:
            page.meta["resource_iri"] = URIRef(page.meta["resource_iri"])
        elif hasattr(page.file, "resource_iri"):
            page.meta["resource_iri"] = page.file.resource_iri
        else:
            base_iri = urlsplit(self.config.base_iri)
            logger.debug(base_iri)
            page.meta["resource_iri"] = URIRef(
                urlunsplit(
                    (
                        base_iri.scheme,
                        base_iri.netloc,
                        str(PurePosixPath(base_iri.path) / page.url),
                        "",
                        "",
                    )
                )
            )
        logger.info(f"Registerd resource_iri: {page.meta['resource_iri']}")
        page.rdf_resource = RDFResource(
            self.graph, page.meta["resource_iri"], self.graph.namespace_manager
        )
        self.resource_iri_to_page[page.meta["resource_iri"]] = page

        # select templates
        if "template" not in page.meta:
            template = TemplateSelectionHelper(
                self.graph,
                self.config.class_template_map,
                self.config.instance_template_map,
            ).get_template_for_resource(page.rdf_resource)
            if template:
                logger.debug(f"Select template: {template} for {page.rdf_resource}")
                page.meta["template"] = template

    def on_env(
        self, env: Environment, config: MkDocsConfig, files: Files, **kwargs
    ) -> Environment | None:
        """Register the jinja filters"""
        register_filters(env)
        env.filters["iri_resolver"] = iri_resolver
        return env

    def on_page_context(
        self,
        context: TemplateContext,
        page: Page,
        config: MkDocsConfig,
        nav: Navigation,
    ) -> TemplateContext:
        """Set the relevant variables for each page."""
        return {**get_context(self.graph, page.rdf_resource), **context}
