from textwrap import dedent

from jinja2 import pass_context
from jinja2.runtime import Context
from rdflib import Graph
from rdflib.resource import Resource as RDFLibResource
from rdflib.term import Identifier, URIRef, Literal
from rdflib.util import from_n3


def set_init_bindings(bindings: dict[str, Identifier]) -> dict[str, URIRef]:
    """Set the init bindings, for a graph.query() call and make sure that no
    blank nodes, i.e. only URIRef and Literal are set."""
    for var, val in bindings.items():
        if isinstance(val, [URIRef, Literal]):
            yield var, val


@pass_context
def sparql_query(
    context: Context, input: RDFLibResource | Graph | URIRef, query: str, **kwargs
):
    if isinstance(input, Graph):
        graph = input
        resourceIri = input.identifier
    if isinstance(input, RDFLibResource):
        graph = input.graph
        resourceIri = input.identifier
    if isinstance(input, URIRef):
        graph = context["graph"]
        resourceIri = input
    namespaces = None
    if context["namespace_manager"]:
        namespaces = dict(context["namespace_manager"].namespaces())
    try:
        return graph.query(
            query,
            initBindings=set_init_bindings(
                {
                    **{k: from_n3(v) for k, v in kwargs.items()},
                    "resourceIri": resourceIri,
                    "resourceUri": resourceIri,
                    "graphIri": graph.identifier,
                }
            ),
            initNs=namespaces,
        )
    except Exception as e:
        raise Exception(
            dedent(f"""There was an issue with your query:
            \"{query}\"
            an the following parameters:
            initBindings: \"{kwargs.items()}\"
            resourceIri: \"{resourceIri}\"
            graphIri: \"{graph.identifier}\"
            namespaces: \"{namespaces}\"

            original exception: {e}
            """)
        )
