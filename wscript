import os.path
from waflib import TaskGen, Task

def configure(conf):
    conf.load('tex')
   # conf.find_program('lualatex')
    conf.find_program('pandoc')
   # conf.env['PDFLATEX'] = conf.env['LUALATEX']

@TaskGen.extension('.pd')
def process_pandoc(self, node):
    bib = getattr(self, 'bibliography', None)
    disabled_exts= getattr(self, 'disable', [])
    if bib:
        bib = self.to_nodes(bib)
        bib_str = "--natbib --bibliography={0}".format(bib[0].path_from(self.bld.bldnode))
    else:
        bib = []
        bib_str = ""
    exts_str = ''.join(map(lambda e: '-'+e, disabled_exts))
    read_format = 'markdown' + exts_str
    out_source = node.change_ext('.latex', '.pd')
    Task.task_factory('pandoc', 
        '${PANDOC} -r ${tsk.read_format} -R -S --latex-engine=xelatex --listings -S -o ${TGT} ${tsk.bib_str} ${SRC[0].abspath()}',
        shell        = False,
        ext_in       = '.pd', 
        ext_out      = '.latex', 
    )
    tsk = self.create_task('pandoc', [node] + bib, out_source)
    tsk.bib_str = bib_str
    tsk.read_format= read_format

def build(bld):
    def source_path(item, ext='.pd'):
        if isinstance(item, basestring):
            return item + ext
        elif isinstance(item, tuple):
            return ' '.join(map(lambda s: os.path.join('ch_' + item[0], 'sec_' + s + ext), item[1]))
        else:
            raise TypeError('Bad source')

    sources = [
        'Introduction',
        #('01', ['Intro', 'Moar']),
        'Conclusion',
    ]
    bld(source=' '.join(map(source_path, sources)), bibliography='bib.bib', disable=['fancy_lists'])

    bld.add_group()

    bld(
        features = 'tex',
        type     = 'xelatex',
        source   = 'main.latex',
        target   = 'main.pdf',
       )
