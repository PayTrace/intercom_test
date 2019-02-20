import json
import os.path
import re
import sys
import yaml

from . import __version__ as _package_version, __name__ as _package, framework

try:
    from docopt_subcommands import command as subcommand, main
    from pick import Picker, pick
except ImportError:
    def main():
        print("Please install with '[cli]' extra (e.g. pip install {}[cli])".format(_package))
    
    def subcommand():
        return lambda fn: fn

class Menu:
    class MenuCanceled(Exception):
        pass
    
    def __init__(self, what_for):
        super().__init__()
        self.what_for = what_for
        def cancel_menu(picker):
            raise self.MenuCanceled()
        self.key_options = [('q', 'quit', cancel_menu)]
    
    def run(self, options):
        return self._run_menu(options)
    
    def _run_menu(self, options):
        title = "\n".join(self._title_lines())
        special_keys = []
        for k, action_desc, handler in self.key_options:
            title += "\n    ({}) to {}".format(k, action_desc)
            special_keys.append((ord(k), handler))
        
        menu = Picker(options, title)
        for special_key in special_keys:
            menu.register_custom_handler(*special_key)
        
        return menu.start()[0]
    
    def _title_lines(self, ):
        return [" Select {} ".format(self.what_for).center(50, "=")]
    
    

class DirPicker(Menu):
    SELECTION_OPTION = "<this directory>"
    
    selected_path = None
    
    def __init__(self, what_for, start_dir='.'):
        super().__init__(what_for)
        self.start_dir = start_dir
        self.rel_path = '.'
        def reset_to_start(picker):
            self.rel_path = '.'
            return '.', -1
        self.key_options.append(('r', 'restart browsing', reset_to_start))
    
    def run(self, ):
        if self.selected_path is not None:
            del self.selected_path
        try:
            while self.selected_path is None:
                step_sel = self._run_menu(self._current_options())
                if step_sel == self.SELECTION_OPTION:
                    self.selected_path = self.rel_path
                else:
                    self.rel_path = os.path.relpath(
                        os.path.normpath(
                            os.path.join(self.start_dir, self.rel_path, step_sel)
                        ),
                        self.start_dir
                    )
        except self.MenuCanceled:
            pass
        return self.selected_path
    
    def _title_lines(self, ):
        tlines = super()._title_lines()
        tlines.append(
            "Currently at {} ({}):".format(
                self.rel_path,
                os.path.abspath(os.path.join(self.start_dir, self.rel_path))
            )
        )
        return tlines
    
    def _current_options(self, ):
        files = []
        dirs = []
        current_dir = os.path.normpath(
            os.path.join(self.start_dir, self.rel_path)
        )
        for e in os.listdir(current_dir):
            (dirs if os.path.isdir(os.path.join(current_dir, e)) else files).append(e)
        
        return [self.SELECTION_OPTION, ".."] + sorted(dirs)

class Config(object):
    """Configuration for command line interface"""
    
    CASE_AUGMENTATION_KEYS = frozenset(('augmentation data', 'request keys'))
    
    case_augmenter = None
    
    def __init__(self, filepath):
        super(Config, self).__init__()
        with open(filepath) as cfgfile:
            cfg_data = yaml.safe_load(cfgfile)
        
        ref_dir = os.path.dirname(filepath)
        
        self.interface_dir = os.path.join(ref_dir, cfg_data['interfaces'])
        self.service_name = cfg_data['service name']
        
        which_aug_keys = self.CASE_AUGMENTATION_KEYS & set(cfg_data.keys())
        if self.CASE_AUGMENTATION_KEYS == which_aug_keys:
            class CLICaseAugmenter(framework.CaseAugmenter):
                pass
            CLICaseAugmenter.CASE_PRIMARY_KEYS = frozenset(cfg_data['request keys'])
            self.case_augmenter = CLICaseAugmenter(
                os.path.join(ref_dir, cfg_data['augmentation data'])
            )
        elif which_aug_keys:
            print("Case augmentation partially specified (only {} given)!".format(
                ', '.join(repr(k) for k in which_aug_keys)
            ), file=sys.stderr)
    
    @classmethod
    def build_with_cui(cls, filepath):
        start_dir = os.path.dirname(filepath)
        ifcs_dir = DirPicker("Interfaces Directory", start_dir).run()
        if ifcs_dir is None:
            return False
        svc_name = Menu("Service Name").run(cls._yaml_files_in_dir(ifcs_dir))
        if svc_name is None:
            return False
        
        augdata_dir = None
        request_keys = ''
        ifc_usage = Menu("Interface Usage").run(['consumer', 'provider'])
        if ifc_usage == 'provider':
            augdata_dir = DirPicker("Augmentation Data Directory", start_dir).run()
            if augdata_dir is not None:
                request_keys = input("What keys are used to specify a request (comma separated list)? ")
        
        with open(filepath, 'w') as cfgfile:
            w = lambda *args, **kwargs: print(*args, file=cfgfile, **kwargs)
            w("interfaces: " + cls._yaml_str(ifcs_dir))
            w("service name: " + cls._yaml_str(svc_name))
            if augdata_dir is not None:
                w()
                w("### These keys configure augmentation data")
                w("request keys: [{}]".format(request_keys))
                w("augmentation data: " + cls._yaml_str(augdata_dir))
        
        return True
    
    @classmethod
    def _yaml_files_in_dir(cls, dirpath):
        files = []
        for e in os.listdir(dirpath):
            if os.path.isfile(os.path.join(dirpath, e)) and e.endswith('.yml'):
                files.append(e[:-4])
        return files
    
    @classmethod
    def _yaml_str(cls, s):
        if "\n" in s:
            raise ValueError("Cannot handle strings with newlines")
        return yaml.dump(s).splitlines()[0]

@subcommand()
def init(options):
    """usage: {program} init [options]
    
    Interactively create a configuration file
    
    Options:
        -c CONFFILE, --config CONFFILE      path to configuration file
    """
    if not Config.build_with_cui(options['--config']):
        print("*** Canceled by user ***")
        raise SystemExit(1)

@subcommand()
def enumerate(options):
    """usage: {program} enumerate [options]
    
    Enumerate all test cases, including any configured augmentation data
    
    Options:
        -c CONFFILE, --config CONFFILE      path to configuration file
        -o FORMAT, --output FORMAT          format of output, e.g. yaml, jsonl [default: yaml]
    """
    config = Config(options.get('--config'))
    
    icp_kwargs = {}
    case_provider = framework.InterfaceCaseProvider(
        config.interface_dir,
        config.service_name,
        case_augmenter=config.case_augmenter,
    )
    
    outfmt = options['--output']
    if outfmt == 'yaml':
        def dump(c):
            print('---')
            yaml.safe_dump(c, sys.stdout)
    elif outfmt == 'jsonl':
        def dump(c):
            print(json.dumps(c))
    else:
        raise ValueError("{!r} is not a supported output format".format(outfmt))
    
    for c in case_provider.cases():
        dump(c)

@subcommand()
def commit_updates(options):
    """usage: {program} commitupdates [options]
    
    Commit the augmentation updates to the compact files
    
    Options:
        -c CONFFILE, --config CONFFILE      path to configuration file
    """
    config = Config(options.get('--config'))
    
    case_provider = framework.InterfaceCaseProvider(
        config.interface_dir,
        config.service_name,
        case_augmenter=config.case_augmenter,
    )
    case_provider.update_compact_files()

def csmain():
    main(sys.argv[0], _package_version)

if __name__ == '__main__':
    my_name = os.path.splitext(os.path.basename(__file__))[0]
    
    # NOTE: Cannot use "python -m{}.{}" as the format string because docopt
    # interprets the "-m..." as flags to the program.
    main("{}.{}".format(_package, my_name), _package_version)
