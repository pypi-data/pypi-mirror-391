# -*- coding: utf-8 -*-
# :Project:   metapensiero.sphinx.d2 — Implement a d2 Sphinx directive
# :Created:   sab 10 ago 2024, 16:45:05
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2024, 2025 Lele Gaifax
#

from __future__ import annotations

from hashlib import md5
from pathlib import Path
from re import finditer
from re import sub
from subprocess import CalledProcessError
from subprocess import PIPE
from subprocess import STDOUT
from subprocess import run
from typing import ClassVar
from typing import TYPE_CHECKING

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.utils import relative_path

from sphinx import errors
from sphinx import addnodes
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective
from sphinx.util.i18n import search_image_for_language
from sphinx.util.nodes import set_source_info


if TYPE_CHECKING:
    from collections.abc import Sequence

    from docutils.nodes import Node
    from sphinx.application import Sphinx
    from sphinx.util.typing import ExtensionMetadata
    from sphinx.util.typing import OptionSpec
    from sphinx.writers.html5 import HTML5Translator
    from sphinx.writers.latex import LaTeXTranslator
    from sphinx.writers.manpage import ManualPageTranslator
    from sphinx.writers.texinfo import TexinfoTranslator
    from sphinx.writers.text import TextTranslator


__version__ = '0.10'
logger = logging.getLogger(__name__)


class D2Error(errors.SphinxError):
    "Something's wrong in a D2 directive"

    category = "D2 error"


def booloption(argument: str) -> bool:
    """A boolean option.

    If no argument, or when its lowercase value is either ``"1"``, ``"true"``, ``"yes"`` or
    ``on``, return ``True``, otherwise ``False``.
    """

    if argument and argument.strip():
        return argument.strip().lower() in ('1', 'true', 'yes', 'on')
    else:
        return True


class d2node(nodes.General, nodes.Inline, nodes.Element):
    """Node holding all details of a d2 diagram, in particular its `code`."""

    def get_location(self) -> str:
        if self.source == self['scriptfn']:
            # Inline script
            return f'{self.source}:{self.line}'
        else:
            return self['scriptfn']

    def collect_internal_refs(self, directive: SphinxDirective) -> None:
        """Collect internal "link" references, that will replaced later at render time."""

        code = self['code']
        chunks = self['code-chunks'] = []
        prevstart = 0
        for link in finditer(r'(?m)^\s*link\s*:\s*(:\w+:.*)$', code):
            start = link.start()
            end = link.end()
            ref = code[link.start(1):end]
            nodes, _ = directive.state.inline_text(sub(r'\s*[^\\]#.*', '', ref), self.line)
            if len(nodes) != 1 or not isinstance(nodes[0], addnodes.pending_xref):
                raise D2Error(f'Invalid link in d2 script at'
                              f' {self.get_location()}:'
                              f' {link.group(0).strip()!r}')
            self += nodes[0]
            chunks.append(code[prevstart:start])
            chunks.append(ref)
            prevstart = end
        if prevstart < len(code):
            chunks.append(code[prevstart:])


def figure_wrapper(directive: SphinxDirective, node: d2node, caption: str) -> nodes.figure:
    figure_node = nodes.figure('', node)
    if 'align' in node:
        figure_node['align'] = node.attributes.pop('align')
    if 'width' in node:
        figure_node['width'] = node.attributes.pop('width')

    inodes, messages = directive.state.inline_text(caption, directive.lineno)
    caption_node = nodes.caption(caption, '', *inodes)
    caption_node.extend(messages)
    set_source_info(directive, caption_node)
    figure_node += caption_node
    return figure_node


class D2Directive(SphinxDirective):
    "Implementation of the ``d2`` directive."

    required_arguments = 0
    optional_arguments = 1
    has_content = True
    final_argument_whitespace = False
    option_spec: ClassVar[OptionSpec] = {
        'align': directives.unchanged,
        'alt': directives.unchanged,
        'caption': directives.unchanged,
        'center': booloption,
        'class': directives.class_option,
        'dark_theme': directives.nonnegative_int,
        'format': lambda arg: directives.choice(arg, ('png', 'svg')),
        'layout': lambda arg: directives.choice(arg, ('dagre', 'elk')),
        'pad': directives.positive_int,
        'redirect_links_to_blank_page': directives.flag,
        'scale': lambda arg: directives.get_measure(arg, ['']),
        'sketch': booloption,
        'theme': directives.nonnegative_int,
        'width': lambda arg: directives.get_measure(arg, directives.length_units + ['%']),
    }

    def run(self) -> Sequence[Node]:
        document = self.state.document
        if self.arguments:
            if self.content:
                return [document.reporter.warning(
                    'Directive d2 cannot have both a content and a filename argument',
                    line=self.lineno)]
            argument = search_image_for_language(self.arguments[0], self.env)
            rel_filename, filename = self.env.relfn2path(argument)
            self.env.note_dependency(rel_filename)
            try:
                with open(filename, encoding='utf-8') as fp:
                    d2code = fp.read()
            except OSError:
                return [document.reporter.warning(
                    f'External d2 file {filename} not found or reading it failed',
                    line=self.lineno)]
        else:
            d2code = '\n'.join(self.content)
            filename = document['source']
            if not d2code.strip():
                return [self.state_machine.reporter.warning(
                    'Ignoring d2 directive without content',
                    line=self.lineno)]

        node = d2node()
        node.source = document['source']
        node.line = self.lineno
        node['scriptfn'] = filename
        node['code'] = d2code
        node.collect_internal_refs(self)

        options = dict(self.options)
        caption = options.pop('caption', None)
        if 'class' in options:
            node['classes'] = options.pop('class')
        for option in ('align', 'alt', 'caption', 'redirect_links_to_blank_page', 'width'):
            if option in options:
                node[option] = options.pop(option)

        node_options = node['options'] = {'docname': self.env.docname}
        node_options.update(options)

        config = self.env.app.config
        for option in self.option_spec:
            cfgopt = f'd2_{option}'
            if option not in node_options and cfgopt in config:
                node_options[option] = config[cfgopt]

        if caption is not None:
            figure = figure_wrapper(self, node, caption)
            self.add_name(figure)
            return [figure]
        else:
            self.add_name(node)
            return [node]


def render_d2(self: HTML5Translator | LaTeXTranslator | TexinfoTranslator,
              node: d2node, fmt: str) -> Path:
    # Expand Sphinx references, replacing them with the respective final URI: given that we are
    # embedding them into the d2 script, that will be rendered in a SVG under the `imagedir`
    # directory, recompute them to be relative to that directory so that the links will be
    # valid, both when we visit the diagram in a webserver and also when we open it on its own,
    # directly from the filesystem
    source_rel_dir = Path(self.document['source']).parent.relative_to(self.builder.srcdir)
    source_target_dir = self.builder.outdir / source_rel_dir
    chunks = node['code-chunks']
    nchunks = len(chunks)
    nchild = 0
    cpos = 1
    while cpos < nchunks:
        ref = node.children[nchild]
        if isinstance(ref, nodes.reference):
            if 'refuri' in ref:
                origuri = uri = ref['refuri']
                if not uri.startswith('/'):
                    reluri, fragment = uri.rsplit('#', 1)
                    uri = relative_path(self.builder.outdir / self.builder.imagedir / 'dummy',
                                        (source_target_dir / reluri).resolve())
                    if fragment:
                        uri += f'#{fragment}'
                uri = uri.replace('#', r'\#')
                chunks[cpos] = f"link: {uri}"
                logger.debug('[d2] replaced refuri %r with %r', origuri, uri)
            elif 'refid' in ref:
                docname = self.builder.env.path2doc(self.document["source"])
                docpath = relative_path(self.builder.outdir / self.builder.imagedir / 'dummy',
                                        (source_target_dir / docname).resolve())
                uri = rf"{docpath}{self.builder.out_suffix}\#{ref['refid']}"
                chunks[cpos] = f"link: {uri}"
                logger.debug('[d2] replaced refid to docname %r with %r', docname, uri)
        else:
            # If the child is not a reference then most probably is a broken link, that Sphinx
            # converted into an inline text: ignore it
            logger.warning('[d2] ignored broken reference link in script at %s: %r',
                           node.get_location(), chunks[cpos])
            chunks[cpos] = ''
        nchild += 1
        cpos += 2

    code = ''.join(chunks).encode('utf-8')
    options = node['options']
    chash = md5(usedforsecurity=False)
    chash.update(code)
    chash.update(str(options).encode('utf-8'))
    fname = chash.hexdigest() + '.' + fmt
    relfn = Path(self.builder.imgpath) / fname
    outfn = Path(self.builder.outdir) / self.builder.imagedir / fname
    if outfn.exists():
        return relfn

    cmd: list[str | Path] = ['d2']
    if options.get('center', False):
        cmd.append('--center')
    if 'layout' in options:
        cmd.append(f"--layout={options['layout']}")
    if 'theme' in options:
        cmd.append(f"--theme={options['theme']}")
    if options.get('sketch', False):
        cmd.append('--sketch')
    if 'pad' in options:
        cmd.append(f"--pad={options['pad']}")
    if 'dark_theme' in options:
        cmd.append(f"--dark-theme={options['dark_theme']}")
    if 'scale' in options:
        cmd.append(f"--scale={options['scale']}")
    cmd.append('-')
    cmd.append(outfn)
    script_dir = Path(node['scriptfn']).parent
    try:
        run(cmd, check=True, input=code, stderr=STDOUT, stdout=PIPE, cwd=script_dir)
    except CalledProcessError as exc:
        shellcmd = ' '.join(str(a) for a in cmd)
        try:
            output = exc.stdout.decode()
        except Exception:
            output = exc.stdout
        logger.warning("Execution of %s failed with status %s\n%s",
                       shellcmd, exc.returncode, output)
        raise D2Error(f"Could not render diagram, d2 exited with status {exc.returncode}")
    except FileNotFoundError:
        shellcmd = ' '.join(str(a) for a in cmd)
        logger.warning("Execution of %s failed, d2 not found", shellcmd)
        raise D2Error("Could not render diagram, d2 not in $PATH")

    if fmt == 'svg' and options.get('redirect_links_to_blank_page', False):
        svg = outfn.read_text()
        outfn.write_text(sub(r'a (href="(?!\w+://)[^"]*")', r'a target="_blank" \1', svg))

    return relfn


def html_visit_d2node(self: HTML5Translator, node: d2node) -> None:
    try:
        relfn = render_d2(self, node, node['options'].get('format', 'svg'))
    except D2Error as err:
        logger.warning(str(err), location=node, type='d2')
        raise nodes.SkipNode
    classes = ' '.join(filter(None, ['d2lang', *node.get('classes', [])]))
    if 'align' in node:
        self.body.append(f'<div align="{node["align"]}" class="align-{node["align"]}">')
    self.body.append('<div class="d2lang">')
    if 'alt' in node:
        alt = node['alt']
    else:
        alt = None
    if node['options']['format'] == 'svg':
        self.body.append(f'<object data="{relfn}" type="image/svg+xml" class="{classes}">\n')
        if alt is not None:
            self.body.append(f'<p class="warning">{self.encode(alt).strip()}</p>')
        self.body.append('</object>\n')
    else:
        if alt is not None:
            alt = f' alt="{self.encode(alt).strip()}"'
        self.body.append(f'<img src="{relfn}" {alt} class="{classes}" />\n')
    self.body.append('</div>\n')
    if 'align' in node:
        self.body.append('</div>\n')

    raise nodes.SkipNode


def latex_visit_d2node(self: LaTeXTranslator, node: d2node) -> None:
    # FIXME: this is COMPLETELY untested
    try:
        relfn = render_d2(self, node, 'png')
    except D2Error as err:
        logger.warning(str(err), location=node, type='d2')
        raise nodes.SkipNode

    is_inline = self.is_inline(node)

    if not is_inline:
        pre = ''
        post = ''
        if 'align' in node:
            if node['align'] == 'left':
                pre = '{'
                post = r'\hspace*{\fill}}'
            elif node['align'] == 'right':
                pre = r'{\hspace*{\fill}'
                post = '}'
            elif node['align'] == 'center':
                pre = r'{\hfill'
                post = r'\hspace*{\fill}}'
        self.body.append('\n%s' % pre)

    self.body.append(r'\sphinxincludegraphics[]{%s}' % relfn)

    if not is_inline:
        self.body.append('%s\n' % post)

    raise nodes.SkipNode


def man_visit_d2node(self: ManualPageTranslator, node: d2node) -> None:
    if 'alt' in node.attributes:
        self.add_text(f'[d2 diagram: {node["alt"]}]')
    else:
        self.add_text('[d2 diagram]')
    raise nodes.SkipNode


def texinfo_visit_d2node(self: TexinfoTranslator, node: d2node) -> None:
    # FIXME: this is COMPLETELY untested
    try:
        relfn = render_d2(self, node, 'png')
    except D2Error as err:
        logger.warning(str(err), location=node, type='d2')
        raise nodes.SkipNode
    self.body.append(f'@image{{{relfn.with_suffix("")},,,[d2lang],png}}\n')
    raise nodes.SkipNode


def text_visit_d2node(self: TextTranslator, node: d2node) -> None:
    if 'alt' in node.attributes:
        self.add_text(f'[d2 diagram: {node["alt"]}]')
    else:
        self.add_text('[d2 diagram]')
    raise nodes.SkipNode


def setup(app: Sphinx) -> ExtensionMetadata:
    from sphinx.config import ENUM

    app.add_directive("d2", D2Directive)
    app.add_node(d2node,
                 html=(html_visit_d2node, None),
                 latex=(latex_visit_d2node, None),
                 man=(man_visit_d2node, None),
                 texinfo=(texinfo_visit_d2node, None),
                 text=(text_visit_d2node, None))

    app.add_config_value('d2_center', False, 'html', [bool],
                         #'Default value for the d2 ``:center:`` option',
                         )
    app.add_config_value('d2_dark_theme', 0, 'html', [bool],
                         #'Default value for the d2 ``:dark_theme:`` option',
                         )
    app.add_config_value('d2_format', 'svg', 'html', ENUM('svg', 'png'),
                         #'Default value for the d2 ``:format:`` option',
                         )
    app.add_config_value('d2_layout', 'dagre', 'html', ENUM('dagre', 'elk'),
                         #'Default value for the d2 ``:layout:`` option',
                         )
    app.add_config_value('d2_pad', 100, 'html', [int],
                         #'Default value for the d2 ``:pad:`` option',
                         )
    app.add_config_value('d2_redirect_links_to_blank_page', True, 'html', [bool],
                         #'Default value for the d2 ``:redirect_links_to_blank_page:`` option',
                         )
    app.add_config_value('d2_scale', -1, 'html', [float,int],
                         #'Default value for the d2 ``:scale:`` option',
                         )
    app.add_config_value('d2_sketch', False, 'html', [bool],
                         #'Default value for the d2 ``:sketch:`` option',
                         )
    app.add_config_value('d2_theme', 0, 'html', [bool],
                         #'Default value for the d2 ``:theme:`` option',
                         )

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
