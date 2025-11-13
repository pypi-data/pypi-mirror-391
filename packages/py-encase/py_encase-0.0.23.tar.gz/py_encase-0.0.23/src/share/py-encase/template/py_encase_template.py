#
# File Template : py_encase.py
#
if False:
    ########## ____STREAMEXTD_TEMPLATE_START____ ##########
    #### ____py_shebang_pattern____ ####
    # -*- coding: utf-8 -*-
    import sys
    import _io
    import collections
    import inspect
    
    class StreamExtd(object):
        """
        Extended I/O Stream Interface
        """
        def __init__(self, 
                     stdin:_io.TextIOWrapper=sys.stdin,
                     stderr:_io.TextIOWrapper=sys.stdout,
                     stdout:_io.TextIOWrapper=sys.stderr):
            streams_t = collections.namedtuple('streams',
                                               ['stdin', 'stdout','stderr'])
            self.streams = streams_t(stdin=self.__class__.StreamIF(sys.stdin),
                                     stderr=self.__class__.StreamIF(sys.stdout),
                                     stdout=self.__class__.StreamIF(sys.stderr))
    
        @property
        def stdin(self):
            return self.streams.stdin
    
        @property
        def stdout(self):
            return self.streams.stdout
    
        @property
        def stderr(self):
            return self.streams.stderr
    
        class StreamIF(object):
            """
            Wrapper for stdout/stderr to show with full qualified function name
            """
            def __init__(self, stream:_io.TextIOWrapper=sys.stderr):
                self.stream = stream
                
            def write(self, text='', *args, cls_name:str=None, more_upper:bool=False):
                refname,lineno = self.caller_fqn(cls_name=cls_name, more_upper=more_upper)
                lhdr   = "[%s:%d] " % (refname, lineno)
                fmttxt = (text % tuple(args)) if len(args)>0 else text
                return self.stream.write(lhdr+(fmttxt if fmttxt.endswith('\n') else fmttxt+'\n'))
            
            def caller_fqn(self, cls_name:str=None, more_upper:bool=False):
                try:
                    if more_upper:
                        frm = inspect.currentframe().f_back.f_back.f_back
                    else:
                        frm = inspect.currentframe().f_back.f_back
        
                    mod_name = frm.f_globals.get('__name__', '')
                    code = frm.f_code
    
                    if sys.version_info >= (3, 11):
                        qualname = code.co_qualname
                    else:
                        if cls_name:
                            qualname = '.'.join([cls_name, code.co_name])
                        else:
                            prntobj = frm.f_locals.get('self') or frm.f_locals.get('cls')
                            if prntobj:
                                qualname = '.'.join([type(prntobj).__name__, code.co_name])
                            else:
                                qualname = code.co_name
        
                    fqn_name = '.'.join([mod_name, qualname, ]) if ( mod_name and mod_name != '__main__' ) else qualname
    
                    return (fqn_name, frm.f_lineno)
    
                finally:
                    del frm
    
    ########## ____STREAMEXTD_TEMPLATE_END____ ##########
    ########## ____STREAMEXTD_TEMPLATE_START____ ##########
    #
    # Show help of class when directly invoked.
    #
    if __name__ == '__main__':
        help(StreamExtd)
    
    ########## ____STREAMEXTD_TEMPLATE_END____ ##########
    ############# ____GITIGNORE_TEMPLATE_START____ #######################
    
    """
    # .gitignore
    *.py[cod]
    *$py.class
    # For emacs backup file
    *~
    {____GIT_INGORE_DIRS____}
    !{____GIT_DUMMYFILE____}
    """
    
    ############# ____GITIGNORE_TEMPLATE_END____ #######################
    
    ############# ____README_TEMPLATE_START____ #######################
        
    """
    #
    # {____TITLE____}
    #
    
    Skeleton for small portable tools by python script
    
    - Contents:
    
    {____contents_lines____}
     
    - Usage (Procedure for adding new script):
    
      1. Put new script under '{____PYLIB_PATH____}'.
    
         Example: '{____PYLIB_PATH____}/{{newscriptname}}.py'
    
      2. Make symbolic link to '{____BIN_PATH____}/{____SHSCRIPT_ENTITY_NAME____}' with same basename as the
         basename of new script.
    
          Example: '{____BIN_PATH____}/{{newscriptname}}' --> {____SHSCRIPT_ENTITY_NAME____}
    
      3. Download external python module by './{____BIN_PATH____}/{____MNGSCRIPT_NAME____}'
    
          Example: '{____PYLIB_PATH____}/{{newscriptname}}.py' uses modules, pytz and tzlocal.
    
          % ./{____BIN_PATH____}/{____MNGSCRIPT_NAME____} install pytz tzlocal
    
      4. Invoke the symbolic link made in step.2 for execute the script.
    
          % ./{____BIN_PATH____}/{{newscriptname}}
    
    - Caution:
    
      - Do not put python scripts/modules that are not managed by pip
        under '{____PIP_PATH____}'.
    
        Otherwise those scripts/modules will be removed by
        `./{____BIN_PATH____}/{____MNGSCRIPT_NAME____} distclean`
    
    - Note:
    
      - Python executable is seeked by the following order.
    
        1. Environmental variable: PYTHON
        2. Shebang in called python script
        3. python3 in PATH
        4. python  in PATH
    
      - pip command is seeked by the following order.
    
        1. Environmental variable: PIP
        2. pip3 in PATH for "{____MNGSCRIPT_NAME____}"
        3. pip3 in PATH
    
    - Requirements (Tools used in "{____SHSCRIPT_ENTITY_NAME____}")
    
      - Python, PIP
    
    - Author
    
      - {____AUTHOR_NAME____} ({____AUTHOR_EMAIL____})
        
    --
    """
    
    ############# ____README_TEMPLATE_END____ #######################
    
    
    ############# ____PY_MAIN_TEMPLATE_START____ #######################
    #### ____py_shebang_pattern____ ####
    # -*- coding: utf-8 -*-
        
    import argparse
    import datetime
    import sys
        
    import pytz
    import tzlocal
    
    #import pkgstruct
    
    class ____SCRIPT_CAPITAL_SYMBOLIZED____(object):
    
        def __init__(self):
            pass
    
        def main(self, args=sys.argv):
            """
            ____SCRIPT_NAME____
            Example code skeleton: Just greeting
            """
            argpsr = argparse.ArgumentParser(description='Example: showing greeting words')
            argpsr.add_argument('name', nargs='*', type=str, default=['World'],  help='your name')
            argpsr.add_argument('-d', '--date', action='store_true', help='Show current date & time')
            args = argpsr.parse_args(args)
            if args.date:
                tz_local = tzlocal.get_localzone()
                datestr  = datetime.datetime.now(tz=tz_local).strftime(" It is \"%c.\"")
            else:
                datestr = ''
    
            print("Hello, %s!%s" % (' '.join(args.name), datestr))
            print("Python : %d.%d.%d " % sys.version_info[0:3]+ "(%s)" % sys.executable)
            hdr_str = "Python path: "
            for i,p in enumerate(sys.path):
                print("%-2d : %s" % (i+1, p))
                hdr_str = ""
        
            #pkg_info   = pkgstruct.PkgStructure(script_path=sys.argv[0])
            #pkg_info.dump(relpath=False, with_seperator=True)
    
    if __name__ == '__main__':
        ____SCRIPT_CAPITAL_SYMBOLIZED____().main()
    
    ########## ____PY_MAIN_TEMPLATE_END____ ##########
    
    
    ########## ____PY_MAIN_APP_FRAMEWORK_TEMPLATE_START____ ##########
    #### ____py_shebang_pattern____ ####
    # -*- coding: utf-8 -*-
        
    import os
    import sys
    import _io
    import collections
    import inspect
    import copy
    import getpass
    
    import pydoc
    import datetime
    import time
    import threading
    
    import argparse_extd
    
    import pkgstruct
    
    import psutil
    import pytz
    import tzlocal
    
    import sshkeyring
    import enc_ds
    
    import plyer
    import streamextd
    
    class ____SCRIPT_CAPITAL_SYMBOLIZED____Framework(streamextd.StreamExtd):
        """
        ____SCRIPT_CAPITAL_SYMBOLIZED____Framework: Skeleton of Application Framework (____SCRIPT_NAME____)
        """
    
        def __init__(self, argv:list=sys.argv, **args):
            super().__init__(**args)
    
            # Sample code to utilize application directory structure
            self.name_invoked = argv[0].removesuffix('.py')
            self.pkg_info     = pkgstruct.PkgStruct(script_path=self.name_invoked)
    
            # Sample code to utilize enciphered data storage
            self.pwdmgr = self.__class__.EncDataMgr(pkg_info=self.pkg_info, **args)
            self.pwdmgr.setup()
                
    
        def main(self, argv:list=sys.argv):
    
            config_name_default = self.pkg_info.script_basename+'.config.json'
            pkg_default_config  = self.pkg_info.concat_path('pkg_statedatadir', 'config', config_name_default)
    
            # Sample code to utilize the extended argument parser (`argparse_extd`)
            #   : loading from / saving to "config file", etc
            argprsr = argparse_extd.ArgumentParserExtd(add_help=True)
            argprsr.load_config(pkg_default_config)
            argprsr.add_argument_config()
            argprsr.add_argument_save_config(default_path=pkg_default_config)
            argprsr.add_argument_verbose()
            argprsr.add_argument_quiet(dest='verbose')
    
            # Add CLI options for the enciphered data storage
            self.pwdmgr.add_argparser_options(arg_parser=argprsr)
    
            argprsr.add_argument('-o', '--output', type=str, help='output filename') 
            argprsr.add_argument('-f', '--dump-format', type=str,
                                 choices=argparse_extd.ArgumentParserExtd.CONFIG_FORMAT,
                                 default='json', help='Output format')
    
            # Example of usual comand-line options 
            argprsr.add_argument('-d', '--date', action='store_true', help='Show current date & time')
            argprsr.add_argument('-D', '--wo-date', action='store_false', dest='date', help='Do not show current date & time')
    
            argprsr.add_argument('-g', '--gui',    action='store_true',              help='GUI mode')
            argprsr.add_argument('-G', '--wo-gui', action='store_false', dest='gui', help='CLI only mode')
    
            # Example of usual comand-line arguments
            argprsr.add_argument('argv', nargs='*', help='Arguments')
    
            # Specify the command-line options/arguments which are not saved into config files 
            arg_opts_not_save = ['--default-config', 'verbose',
                                 '--output', '--save-config', 'gui', 'argv'] 
            arg_opts_not_save += self.pwdmgr.ls_argparser_attrs()
            argprsr.append_write_config_exclude(arg_opts_not_save)
        
            # Parse command-line arguments
            args = argprsr.parse_args(argv, action_help=False)
    
            # Save command-line options into config file
            argprsr.save_config_action()
            # Additional saving of configuration according to CL option
            argprsr.write_config(argprsr.args.output)
    
            # Example to manipurate the enciphered data storage
            if self.pwdmgr.manage_auth_password(args=argprsr.args):
                return
    
            #
            # Examples to correct the run-time / running-environment info.
            # 
            app_info = {'Python': ( "%d.%d.%d" % sys.version_info[0:3]
                                    +" (%s)" % sys.executable),
                        'Argv'  : ' '.join(args.argv)}
            KEYWORDS = ['pkg_name', 'pkg_path', 'prefix']
            app_info.update({ k: self.pkg_info[k] for k in KEYWORDS })
    
            tz_local = tzlocal.get_localzone()
            mech_info  = f'CPU Usage: {psutil.cpu_percent(interval=1)} %'
            mech_info += f', Load Avg. = {psutil.getloadavg()[0]:.2f}'
            if argprsr.args.date:
                mech_info += f' @ {datetime.datetime.now(tz=tz_local).strftime("%c")}'
            else:
                mech_info += f' @ {datetime.datetime.now().strftime("%c")}'
            app_info.update({'MECH': mech_info })
    
            #
            # Example codes for non-GUI (CLI) environment
            # 
            if not argprsr.args.gui:
                for k,v in app_info.items():
                    self.stdout.write(("%-9s %s" % (str(k)+':', v)).replace('%', '%%'))
                return
    
            #
            # Example codes for GUI application by KIVY
            # 
            # Suppress parsing command-line arguments by KIVY
            os.environ['KIVY_NO_ARGS'] = '1'
            # Specify the working directory of KIVY
            self.pkg_info.make_subdirs('pkg_sysconfdir', 0o755, True, 'kivy')
            os.environ['KIVY_HOME'] = self.pkg_info.concat_path('pkg_sysconfdir', 'kivy')
            # Control the standard output by KIVY
            if not argprsr.args.verbose:
                os.environ['KIVY_NO_CONSOLELOG'] = '1'
            # Specify the location of log output by KIVY
            import kivy.config
            kivy.config.Config.set("kivy", "log_dir", self.pkg_info.pkg_logdir)
            # Load kivy module here otherwise the KIVY settings above is not effective.
            import kivy.app
            import kivy.uix.widget
            import kivy.properties
            # Specify the KV file to be loaded.
            kv_dir=self.pkg_info.pkg_runstatedir
            kv_file=self.pkg_info.concat_path('pkg_datadir',
                                              os.path.basename(self.name_invoked)+'.kv')
            # Define Application clase by inheriting `kivy.app.App`
            class MainGUIApp(kivy.app.App):
    
                def __init__(self, app_info, kv_dir, **kwargs):
                    super().__init__(kv_directory=kv_dir, **kwargs)
                    self.app_info = app_info
                    
                # Sample code to utilize "notify" by plyer module
                def notify(self, **args):
                    print (args)
                    ntfctn_thread = threading.Thread(target=plyer.notification.notify, 
                                                     kwargs=args)
                    ntfctn_thread.start()
    
            # Define Main Widget by inheriting `kivy.uix.widget.Widget`
            class MainWidget(kivy.uix.widget.Widget):
    
                KEYWORDS = ['pkg_name', 'pkg_path', 'prefix', 'MECH', 'Python', 'Argv']
        
                status_text = { x: kivy.properties.StringProperty() for x in KEYWORDS }
    
                def __init__(self, **kwargs):
                    super().__init__(**kwargs)
                    for x in self.KEYWORDS:
                        self.status_text[x] = kivy.app.App.get_running_app().app_info[x]
    
            # Create the instance of GUI application class
            main_app = MainGUIApp(app_info=app_info, kv_dir=kv_dir, kv_file=kv_file)
    
            # Sample code to utilize "notify" by plyer module
            main_app.notify(title='Application start', 
                            message=app_info['MECH'],
                            app_name=app_info['pkg_name'],
                            timeout=10)
    
            # Start main-loop of the GUI application instance
            main_app.run()
    
    
        # Example of the enciphered data storage
        class EncDataMgr(enc_ds.EncDataStorage):
            """
            EncDataMgr: Storing HTTP passwords
            """
    
            def __init__(self, pkg_info:pkgstruct.PkgStruct, **args):
                self.conf = {
                    'storage_name':            pkg_info.script_basename,
                    'storage_masterkey':       pkg_info.script_basename + 'AburaKataBura',
                    'data_identifier':         pkg_info.script_basename + '_config',
                    'key_id':                  pkg_info.script_basename+"@"+'host.jp',
                    'key_bits':                4096, # 8192,
                    'key_file_basename':       'id_rsa_'+pkg_info.script_basename,
                    'keypath_prefix':          pkg_info.concat_path('pkg_sysconfdir', 'pki'),
                }
                self.conf.update(dict(args))
                super().__init__(**self.conf)
                self.io_format = 'json'
                self.path      = pkg_info.concat_path('pkg_statedatadir', 'auth', 
                                                      'auth_data.' + self.io_format)
                return
    
            def setup(self, **args):
                """
                Setup the SSHKeyring and Initial Data structure
                """
                empty_data = { self.conf['data_identifier']: {'auth_info': {}}}
                self.setup_sshkeyinfo()
                # self.set_cipher_unit()
                self.set_datatree(base_obj=args.get('init_data', empty_data))
                if os.path.exists(self.path):
                    self.read_datatree(update=True, getall=True,
                                       decipher=False, decipher_entire_data=True)
                    self.decipher(entire_data=True, verbose=False)
                return
    
            def save(self):
                """
                Saving the enciphered data to file
                """
                self.encipher(entire_data=True, verbose=False)
                self.save_datatree()
                self.decipher(entire_data=True, verbose=False)
                return
    
            def add_argparser_options(self, arg_parser):
                """
                Define Command-line arguments for manipurating the enciphered data
                """
                arg_parser.add_argument('--set-password',  action='store_true', help='Set password mode')
                arg_parser.add_argument('--erase-password', action='store_true', help='Set password mode')
                arg_parser.add_argument('--dump-password', action='store_true', help='Show password mode')
                arg_parser.add_argument('-u', '--user', help='http/https auth username')
                arg_parser.add_argument('-p', '--password', help='http/https auth password')
                arg_parser.add_argument('-U', '--url', help='URL to set password')
                return
    
            def ls_argparser_attrs(self):
                """
                List of Command-line arguments so that it can be used for
                 argparse_extd.ArgumentParserExtd.append_write_config_exclude()
                """
                return ['--set-password', 
                        '--erase-password',
                        '--dump-password',
                        '--user', '--password', '--url']
    
            def store_auth_password(self, args):
                """
                Add data to the data_tree for enciphered_data
                """
                usr = args.user if hasattr(args, 'user') else ''
                url = args.url  if hasattr(args, 'url')  else ''
                pswd = (args.password 
                        if (hasattr(args, 'password') and args.password )
                        else  getpass.getpass(prompt=f'Password for {usr}@{url}: '))
                buf = {'url': url, 'user': usr, 'password': pswd }
                node_key = (self.conf['data_identifier'], 'auth_info', )
                if not url:
                    return -1
    
                if self.datatree.is_validkey(keyset=node_key,
                                             leaf_node=False, negate=True):
                    self.datatree[node_key] = {}
    
                self.datatree[node_key].update({(url,usr): buf})
    
                return 0
    
            def erase_auth_password(self, args, url=None, user=None):
                """
                Erase data from the data_tree for enciphered_data
                """
                url = ( url if url  else
                        (args.url  if hasattr(args, 'url')  else ''))
    
                usr = ( user if user  else
                        (args.user  if hasattr(args, 'user')  else ''))
    
                parent_key = (self.conf['data_identifier'], 'auth_info')
                node_key   = parent_key+((url,usr),)
    
                if not url:
                    return -1
    
                if self.datatree.is_validkey(keyset=node_key,
                                             leaf_node=False, negate=True):
                    return -1
    
                self.datatree[parent_key].pop( (url,usr) )
                return 0
    
            def dump_auth_password(self, args):
                """
                Example of accessing data from the data_tree for enciphered_data
                """
                node_key = (self.conf['data_identifier'], 'auth_info',)
                for k,v in self.datatree[node_key].items():
                    print(k, v)
                return 0
    
            def manage_auth_password(self, args):
                """
                Define the application behavior to manipulate the enciphered data storage
                Return status := True if the defined procedure has been executed 
                                      else False
                """
                if hasattr(args, 'set_password') and args.set_password:
                    status = self.store_auth_password(args=args)
                    if status:
                        if hasattr(args, 'verbose') and args.verbose:
                            sys.stderr.write(f'Set-password Error: status=={status}\n')
                    else:
                        self.save()
                    return True
                if hasattr(args, 'erase_password') and args.erase_password:
                    status = self.erase_auth_password(args, url=None, user=None)
                    if status:
                        if hasattr(args, 'verbose') and args.verbose:
                            sys.stderr.write(f'Erase-password Error: status=={status}\n')
                    else:
                        p_key = (self.conf['data_identifier'], 'auth_info')
                        
                        print (self.datatree[p_key])
    
                        if len(self.datatree[p_key])<1:
                            if hasattr(args, 'verbose') and args.verbose:
                                sys.stderr.write(f'Erase-password: No password data remaining. Remove file : {self.path}\n')
                            if hasattr(args, 'dry_run') and args.dry_run:
                                sys.stderr.write(f'os.remove({self.path})\n')
                            else:
                                os.remove(self.path)
                        else:
                            self.save()
    
                    return True
    
                if args.dump_password:
                    self.dump_auth_password(args)
                    return True
    
                return False
    
    #
    # Invoke the main routine when this file is executed
    #    
    if __name__ == '__main__':
        ____SCRIPT_CAPITAL_SYMBOLIZED____Framework().main()
    
    ########## ____PY_MAIN_APP_FRAMEWORK_TEMPLATE_END____ ##########
    
    
    ########## ____PY_MAIN_KVFILE_TEMPLATE_START____ ##########
    """
    # -*- mode: kivy; -*-
    #
    # Kivy Widget definition: ____APPNAME____
    #
    MainWidget:
    
    <MainWidget>:
        BoxLayout:
            orientation: 'vertical'
            size: self.parent.size
    
            BoxLayout:
                size_hint: 1.0, 0.85
                orientation: 'vertical'
    
                BoxLayout:
                    size_hint: 1.0, 0.2
                    Label:
                        id: status_label_Python
                        size_hint: 0.2, 1.0
                        text_size: self.size
                        halign: 'center'
                        valign: 'middle'
    
                        text: 'Python'
    
                    Label:
                        id: status_text_Python
                        size_hint: 0.8, 1.0
                        text_size: self.size
                        halign: 'left'
                        valign: 'middle'
    
                        text: root.status_text['Python']
                BoxLayout:
                    size_hint: 1.0, 0.2
                    Label:
                        id: status_label_Argv
                        size_hint: 0.2, 1.0
                        text_size: self.size
                        halign: 'center'
                        valign: 'middle'
    
                        text: 'Argv'
    
                    Label:
                        id: status_text_Argv
                        size_hint: 0.8, 1.0
                        text_size: self.size
                        halign: 'left'
                        valign: 'middle'
    
                        text: root.status_text['Argv']
    
                BoxLayout:
                    size_hint: 1.0, 0.2
                    Label:
                        id: status_label_MECH
                        size_hint: 0.2, 1.0
                        text_size: self.size
                        halign: 'center'
                        valign: 'middle'
    
                        text: 'MECH'
    
                    Label:
                        id: status_text_MECH
                        size_hint: 0.8, 1.0
                        text_size: self.size
                        halign: 'left'
                        valign: 'middle'
    
                        text: root.status_text['MECH']
                        
                BoxLayout:
                    size_hint: 1.0, 0.2
                    Label:
                        id: status_label_pkg_name
                        size_hint: 0.2, 1.0
                        text_size: self.size
                        halign: 'center'
                        valign: 'middle'
    
                        text: 'pkg_name'
                        
                    Label:
                        id: status_text_pkg_name
                        size_hint: 0.8, 1.0
                        text_size: self.size
                        halign: 'left'
                        valign: 'middle'
    
                        text: root.status_text['pkg_name']
        
                BoxLayout:
                    size_hint: 1.0, 0.2
                    Label:
                        id: status_label_pkg_path
                        size_hint: 0.2, 1.0
                        text_size: self.size
                        halign: 'center'
                        valign: 'middle'
    
                        text: 'pkg_path'
    
                    Label:
                        id: status_text_pkg_path
                        size_hint: 0.8, 1.0
                        text_size: self.size
                        halign: 'left'
                        valign: 'middle'
    
                        text: root.status_text['pkg_path']
        
                BoxLayout:
                    size_hint: 1.0, 0.2
                    Label:
                        id: status_label_prefix
                        size_hint: 0.2, 1.0
                        text_size: self.size
                        halign: 'center'
                        valign: 'middle'
    
                        text: 'prefix'
    
                    Label:
                        id: status_text_prefix
                        size_hint: 0.8, 1.0
                        text_size: self.size
                        halign: 'left'
                        valign: 'middle'
    
                        text: root.status_text['prefix']
    
            Button:
                size_hint: 1.0, 0.05
                text: "Quit"
                on_press: app.stop()
    
        
    """
    ########## ____PY_MAIN_KVFILE_TEMPLATE_END____ ##########
    
    ########## ____PY_LIB_SCRIPT_TEMPLATE_START____ ##########
    #### ____py_shebang_pattern____ ####
    # -*- coding: utf-8 -*-
    
    import json
    
    class ____NEW_CLS_NAME____(object):
        """
        ____NEW_CLS_NAME____
        Example class code skeleton: 
        """
        def __init__(self):
            self.contents = {}  
    
        def __repr__(self):
            return json.dumps(self.contents, ensure_ascii=False, indent=4, sort_keys=True)
    
        def __str__(self):
            return json.dumps(self.contents, ensure_ascii=False, indent=4, sort_keys=True)
    
    if __name__ == '__main__':
        help(____NEW_CLS_NAME____)
    
    ########## ____PY_LIB_SCRIPT_TEMPLATE_END____ ##########
    
    ########## ____PKG_CACHE_TEMPLATE_START____ ##########
    #### ____py_shebang_pattern____ ####
    # -*- coding: utf-8 -*-
    import gzip
    import bz2
    import re
    import os
    import sys
    import json
    import filecmp
    
    import yaml
    
    import intrinsic_format
    import pkgstruct
    
    class PkgCache(pkgstruct.PkgStruct):
        """
        Class for Data cache for packaged directory
        """
        def __init__(self, subdirkey='pkg_cachedir', subdir=None, 
                     dir_perm=0o755, perm=0o644, keep_oldfile=False, backup_ext='.bak',
                     timestampformat="%Y%m%d_%H%M%S", avoid_duplicate=True,
                     script_path=None, env_input=None, prefix=None, pkg_name=None,
                     flg_realpath=False, remove_tail_digits=True, remove_head_dots=True, 
                     basename=None, tzinfo=None, unnecessary_exts=['.sh', '.py', '.tar.gz'],
                     namespece=globals(), yaml_register=True, **args):
    
            super().__init__(script_path=script_path, env_input=env_input, prefix=prefix, pkg_name=pkg_name,
                             flg_realpath=flg_realpath, remove_tail_digits=remove_tail_digits, remove_head_dots=remove_head_dots, 
                             unnecessary_exts=unnecessary_exts, **args)
    
            self.config = { 'dir_perm':                 dir_perm,
                            'perm':                     perm,
                            'keep_oldfile':             keep_oldfile,
                            'backup_ext':               backup_ext,
                            'timestampformat':          timestampformat,
                            'avoid_duplicate':          avoid_duplicate,
                            'json:skipkeys':            False,
                            'json:ensure_ascii':        False, # True,
                            'json:check_circular':      True, 
                            'json:allow_nan':           True,
                            'json:indent':              4, # None,
                            'json:separators':          None,
                            'json:default':             None,
                            'json:sort_keys':           True, # False,
                            'json:parse_float':         None,
                            'json:parse_int':           None,
                            'json:parse_constant':      None,
                            'json:object_pairs_hook':   None,
                            'yaml:stream':              None,
                            'yaml:default_style':       None,
                            'yaml:default_flow_style':  None,
                            'yaml:encoding':            None,
                            'yaml:explicit_start':      True, # None,
                            'yaml:explicit_end':        True, # None,
                            'yaml:version':             None,
                            'yaml:tags':                None,
                            'yaml:canonical':           True, # None,
                            'yaml:indent':              4, # None,
                            'yaml:width':               None,
                            'yaml:allow_unicode':       None,
                            'yaml:line_break':          None
                           }
    
            if isinstance(subdir,list) or isinstance(subdir,tuple):
                _subdir = [ str(sd) for sd in subdir]
                self.cache_dir = self.concat_path(skey, *_subdir)
            elif subdir is not None:
                self.cache_dir = self.concat_path(skey, str(subdir))
            else:
                self.cache_dir = self.concat_path(skey)
    
            self.intrinsic_formatter = intrinsic_format.intrinsic_formatter(namespace=namespace,
                                                                            register=yaml_register)
    
        def read(self, fname, default=''):
            return self.read_cache(fname, default='', directory=self.cache_dir)
    
        def save(self, fname, data):
            return self.save_cache(fname, data, directory=self.cache_dir, **self.config)
    
        @classmethod
        def save_cache(cls, fname, data, directory='./cache', dir_perm=0o755,
                       keep_oldfile=False, backup_ext='.bak', 
                       timestampformat="%Y%m%d_%H%M%S", avoid_duplicate=True):
            """ function to save data to cache file
            fname     : filename
            data      : Data to be stored
            directory : directory where the cache is stored. (default: './cache')
        
            Return value : file path of cache file
                           None when fail to make cache file
            """
            data_empty = True if (((isinstance(data, str) or isinstance(data, bytes) or
                                    isinstance(data, dict) or isinstance(data, list) or
                                    isinstance(data, tuple) ) and len(data)==0)
                                  or isinstance(data, NoneType) ) else False
            if data_empty:
                return None
            if not os.path.isdir(directory):
                os.makedirs(directory, mode=dir_perm, exist_ok=True)
            o_path = os.path.join(directory, fname)
            ext1, ext2, fobj = cls.open_autoassess(o_path, 'w',
                                                   keep_oldfile=keep_oldfile,
                                                   backup_ext=backup_ext, 
                                                   timestampformat=timestampformat,
                                                   avoid_duplicate=avoid_duplicate)
            if fobj is None:
                return None
    
            if ext2 == 'yaml':
                #f.write(yaml.dump(data))
                f.write(self.intrinsic_formatter.dump_json(data, 
                                                           skipkeys=self.config['json:skipkeys'],
                                                           ensure_ascii=self.config['json:ensure_ascii'],
                                                           check_circular=self.config['json:check_circular'],
                                                           allow_nan=self.config['json:allow_nan'],
                                                           indent=self.config['json:indent'],
                                                           separators=self.config['json:separators'],
                                                           default=self.config['json:default'],
                                                           sort_keys=self.config['json:sort_keys']))
            elif ext2 == 'json':
                #f.write(json.dumps(data, ensure_ascii=False))
                f.write(self.intrinsic_formatter.dump_yaml(data,
                                                           stream=self.config['yaml:stream'],
                                                           default_style=self.config['yaml:default_style'],
                                                           default_flow_style=self.config['yaml:default_flow_style'],
                                                           encoding=self.config['yaml:encoding'],
                                                           explicit_start=self.config['yaml:explicit_start'],
                                                           explicit_end=self.config['yaml:explicit_end'],
                                                           version=self.config['yaml:version'],
                                                           tags=self.config['yaml:tags'],
                                                           canonical=self.config['yaml:canonical'],
                                                           indent=self.config['yaml:indent'],
                                                           width=self.config['yaml:width'],
                                                           allow_unicode=self.config['yaml:allow_unicode'],
                                                           line_break=self.config['yaml:line_break']))
            else:
                f.write(data)
            f.close()
    
            os.path.chmod(o_path, mode=perm)
            return o_path
    
        @classmethod
        def backup_by_rename(cls, orig_path, backup_ext='.bak',
                             timestampformat="%Y%m%d_%H%M%S", avoid_duplicate=True):
            if not os.path.lexists(orig_path):
                return
            path_base, path_ext2 = os.path.splitext(orig_path)
            if path_ext2 in ['.bz2', '.gz']:
                path_base, path_ext = os.path.splitext(path_base)
            else:
                path_ext2, path_ext = ('', path_ext2)
            if path_ext == backup_ext and len(path_base)>0:
                path_base, path_ext = os.path.splitext(path_base)
            if isinstance(timestampformat, str) and len(timestampformat)>0:
                mtime_txt = '.' + datetime.datetime.fromtimestamp(os.lstat(orig_path).st_mtime).strftime(timestampformat)
            else:
                mtime_txt = ''
    
            i=0
            while(True):
                idx_txt = ( ".%d" % (i) ) if i>0 else ''
                bak_path = path_base + mtime_txt + idx_txt + path_ext  + backup_ext + path_ext2
                if os.path.lexists(bak_path):
                    if avoid_duplicate and filecmp.cmp(orig_path, bak_path, shallow=False):
                        os.unlink(bak_path)
                    else:
                        continue
                os.rename(orig_path, bak_path)
                break
    
                
        @classmethod
        def open_autoassess(cls, path, mode, 
                            keep_oldfile=False, backup_ext='.bak', 
                            timestampformat="%Y%m%d_%H%M%S", avoid_duplicate=True):
    
            """ function to open normal file or file compressed by gzip/bzip2
                path : file path
                mode : file open mode 'r' or 'w'
        
                Return value: (1st_extension: bz2/gz/None,
                               2nd_extension: yaml/json/...,
                               opend file-io object or None)
            """
            if 'w' in mode or 'W' in mode:
                modestr = 'w'
                if keep_oldfile:
                    cls.backup_by_rename(path, backup_ext=backup_ext,
                                         timestampformat=timestampformat,
                                         avoid_duplicate=avoid_duplicate)
            elif 'r' in mode  or 'R' in mode:
                modestr = 'r'
                if not os.path.isfile(path):
                    return (None, None, None)
            else:
                raise ValueError("mode should be 'r' or 'w'")
    
            base, ext2 = os.path.splitext(path)
            if ext2 in ['.bz2', '.gz']:
                base, ext1 = os.path.splitext(path_base)
            else:
                ext1, ext2 = (ext2, '')
    
            if ext2 == 'bz2':
                return (ext2, ext1, bz2.BZ2File(path, modestr+'b'))
            elif ext2 == 'gz':
                return (ext2, ext1, gzip.open(path, modestr+'b'))
            return (ext2, ext1, open(path, mode))
    
        @classmethod
        def read_cache(cls, fname, default='', directory='./cache'):
            """ function to read data from cache file
            fname      : filename
            default   : Data when file is empty (default: empty string)
            directory : directory where the cache is stored. (default: ./cache)
        
            Return value : data    when cache file is exist and not empty,
                           default otherwise
            """
            if not os.path.isdir(directory):
                return default
            in_path = os.path.join(directory, fname)
            ext1, ext2, fobj = cls.open_autoassess(in_path, 'r')
            if fobj is None:
                return default
            f_size = os.path.getsize(in_path)
    
            data = default
            if ((ext1 == 'bz2' and f_size > 14) or
                (ext1 == 'gz'  and f_size > 14) or
                (ext1 != 'bz2' and ext1 != 'gz' and f_size > 0)):
                if ext2 == 'yaml' or ext2 == 'YAML':
                    #data = yaml.load(fobj)
                    data = self.intrinsic_formatter.load_json(fobj,
                                                              parse_float=self.config['json:parse_float'],
                                                              parse_int=self.config['json:parse_int'],
                                                              parse_constant=self.config['json:parse_constant'],
                                                              object_pairs_hook=self.config['json:object_pairs_hook'])
                elif ext2 == 'json'or ext2 == 'JSON':
                    # data = json.load(fobj)
                    data = self.intrinsic_formatter.load_yaml(fobj)
                else:
                    data = fobj.read()
            f.close()
            return data
        
    
    if __name__ == '__main__':
        help(PkgCache)
    
    ########## ____PKG_CACHE_TEMPLATE_END____ ##########
    
    ########## ____INTRINSIC_FORMATTER_TEMPLATE_START____ ##########
    #### ____py_shebang_pattern____ ####
    # -*- coding: utf-8 -*-
    import os
    import sys
    import io
    
    import datetime
    import copy
    import inspect
    
    import json
    import yaml
    
    class intrinsic_formatter(object):
        """
        Utility for intrinsic format to store/restore class instanse data.
                w/  interface for PyYAML and json
        """
        def __init__(self, namespace=globals(), register=True, proc=None):
            self.pyyaml_dumper  = yaml.SafeDumper
            self.pyyaml_loader  = yaml.SafeLoader
            self.namespace      = namespace
            self.proc           = proc
            if register:
                self.pyyaml_register(namespace=self.namespace)
    
        @classmethod
        def decode(cls, data, proc=None, namespace=globals()):
            """
            Restore object from intrinsic data expression as much as possible
            """
            untouch_type  = (int, float, complex, bool, str, bytes, bytearray)
            sequence_type = (list, tuple, set, frozenset)
        
            if isinstance(data, dict):
                meta_data_tag = ('____class____', '____name____', '____tag____')
                _cls_, _clsname, _clstag = ( data.get(k) for k in meta_data_tag )
                if _cls_ == 'datetime.datetime':
                    # return datetime.datetime.fromisoformat(data.get('timestamp'))
                    return datetime.datetime.strptime(data.get('timestamp'), '%Y-%m-%dT%H:%M:%S.%f%z')
        
                if _cls_ is not None and _clsname is not None and _clstag is not None:
                    if isinstance(namespace, dict):
                        cls_ref = namespace.get(_cls_)
                        if cls_ref is None:
                            cls_ref = namespace.get(_clsname)
                    if cls_ref is None:
                        cls_ref = locals().get(_cls_)
                    if cls_ref is None:
                        cls_ref = locals().get(_clsname)
                    if cls_ref is None:
                        cls_ref = globals().get(_cls_)
                    if cls_ref is None:
                        cls_ref = globals().get(_clsname)
                    if cls_ref is not None and inspect.isclass(cls_ref):
                        if hasattr(cls_ref, 'from_intrinsic') and callable(cls_ref.from_intrinsic):
                            return proc(cls_ref.from_intrinsic(data)) if callable(proc) else cls_ref.from_intrinsic(data)
                        if hasattr(cls_ref, 'from_dict') and callable(cls_ref.from_dict):
                            return proc(cls_ref.from_dict(data)) if callable(proc) else cls_ref.from_dict(data)
        
                        cnstrctr_args={k: cls.decode(d, proc=proc, namespace=namespace) for k, d in data.items() if k not in meta_data_tag }
                        try:
                            new_obj=cls_ref()
                            for k,d in cnstrctr_args.items():
                                new_obj.__dict__[k] = copy.deepcopy(d)
                            return new_obj
                        except:
                            pass
                return {k: cls.decode(d, proc=proc, namespace=namespace) for k, d in data.items() }
        
            for _seqtype in sequence_type:
                if isinstance(data, _seqtype):
                    return _seqtype( cls.decode(d, proc=proc) for d in data )
        
            if isinstance(data, untouch_type):
                return proc(data) if callable(proc) else data
        
            #if data is None:
            #    return None
        
            return proc(data) if callable(proc) else data
        
        @classmethod
        def encode(cls, data, proc=None):
            """
            Convert object to intrinsic data expression as much as possible
            """
        
            untouch_type  = (int, float, complex, bool, str, bytes, bytearray)
            sequence_type = (list, tuple, set, frozenset)
            undump_keys   = ('__init__', '__doc__' )
            # undump_keys   = ('__module__', '__init__', '__doc__' )
        
            if data is None:
                return None
        
            if isinstance(data, untouch_type):
                return proc(data) if callable(proc) else data
        
            if isinstance(data, datetime.datetime):
                return {'____class____': data.__class__.__module__+'.'+data.__class__.__name__,
                        '____name____':  data.__class__.__name__,
                        '____tag____':  '!!'+data.__class__.__name__,
                        #'timestamp': data.isoformat(timespec='microseconds'),
                        'timestamp': data.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),  }
        
            if isinstance(data, dict):
                return {k: cls.encode(d, proc=proc) for k,d in data.items() }
        
            for _seqtype in sequence_type:
                if isinstance(data, _seqtype):
                    return _seqtype( cls.encode(d, proc=proc) for d in data )
        
            if ( isinstance(data,object) and
                 ( not inspect.ismethod(data) ) and 
                 ( not inspect.isfunction(data) ) ):
                try:
                    meta_data = {'____class____': data.__class__.__module__+'.'+data.__class__.__name__,
                                 '____name____':  data.__class__.__name__,
                                 '____tag____':  '!!'+data.__class__.__name__}
                    if hasattr(data, 'intrinsic_form') and callable(data.intrinsic_form):
                        return { **meta_data, **(data.intrinsic_form()) }
                    elif hasattr(data, 'to_dict') and callable(data.to_dict):
                        return { **meta_data, **(data.to_dict()) }
                    elif hasattr(data, 'asdict') and callable(data.asdict):
                        return { **meta_data, **(data.asdict()) }
        
                    _data_dict_=data.__dict__
                    return { **meta_data,
                             **{ k: cls.encode(d, proc=proc) 
                                 for k, d in _data_dict_.items()
                                 if ( ( k not in undump_keys ) and
                                      ( isinstance(d,object) and
                                        ( not inspect.ismethod(d) ) and 
                                        ( not inspect.isfunction(d) ) ) ) } }
                except:
                    return proc(data) if callable(proc) else data
        
            return None
    
        @classmethod
        def pyyaml_extended_representer(cls, dumper, obj):
            cnved = cls.encode(obj)
            node = dumper.represent_mapping(cnved.get('____tag____'), cnved)
            return node
    
        def pyyaml_register_presenter(self, namespace=globals()):
            apathic_keys = ('__name__', '__doc__', '__package__', '__loader__', '__spec__',
                            '__annotations__', '__builtins__', '__module__', '__init__')
            if isinstance(namespace, dict):
                glbs = {clskey: cls for clskey, cls in namespace.items()
                        if inspect.isclass(cls) and clskey not in apathic_keys }
                tag_tbd = [ str(cls.__name__) for key,cls in glbs.items() ]
                for i_tag in tag_tbd:
                    self.pyyaml_dumper.add_representer(namespace.get(i_tag), intrinsic_formatter.pyyaml_extended_representer)
            else:            
                glbs = {clskey: cls for clskey, cls in globals().items()
                        if inspect.isclass(cls) and clskey not in apathic_keys }
                tag_tbd = [ str(cls.__name__) for key,cls in glbs.items() ]
                for i_tag in tag_tbd:
                    self.pyyaml_dumper.add_representer(globals()[i_tag], intrinsic_formatter.pyyaml_extended_representer)
    
        @classmethod
        def pyyaml_node_to_dict(cls, loader, node):
            if isinstance(node, yaml.nodes.SequenceNode):
                ret = loader.construct_sequence(node)
                for idx, sub_node in enumerate(node.value):
                    if isinstance(sub_node, yaml.nodes.CollectionNode):
                        ret[idx] = cls.pyyaml_node_to_dict(loader, sub_node)
            elif isinstance(node, yaml.nodes.MappingNode):
                ret = loader.construct_mapping(node)
                for sub_key, sub_node in node.value:
                    if isinstance(sub_node, yaml.nodes.CollectionNode):
                        ret[sub_key.value] = cls.pyyaml_node_to_dict(loader, sub_node)
            else:
                ret = loader.construct_scalar(node)
            return ret
    
        @classmethod
        def pyyaml_extended_constructor(cls, loader, node, proc=None, namespace=globals()):
            deced = cls.pyyaml_node_to_dict(loader, node)
            obj = cls.decode(deced, proc=proc, namespace=namespace)
            return obj
    
        def pyyaml_register_constructor(self, namespace=globals()):
            apathic_keys = ('__name__', '__doc__', '__package__', '__loader__', '__spec__',
                            '__annotations__', '__builtins__', '__module__', '__init__')
            if namespace is None:
                glbs = {clskey: cls for clskey, cls in globals().items()
                        if inspect.isclass(cls) and clskey not in apathic_keys }
                tag_tbd = [ '!!'+str(cls.__name__) for key,cls in glbs.items() ]
            elif isinstance(namespace, (list, tuple, set, frozenset)):
                tag_tbd = namespace
            elif isinstance(namespace, dict):
                glbs = {clskey: cls for clskey, cls in namespace.items()
                        if inspect.isclass(cls) and clskey not in apathic_keys }
                tag_tbd = [ '!!'+str(cls.__name__) for key,cls in glbs.items() ]
            else:
                tag_tbd = [ namespace ]
    
            for i_tag in tag_tbd:
                self.pyyaml_loader.add_constructor(i_tag,
                                                   lambda l, n : intrinsic_formatter.pyyaml_extended_constructor(l, n,
                                                                                                                 proc=self.proc,
                                                                                                                 namespace=self.namespace))
    
        def pyyaml_register(self, namespace=globals()):
            self.pyyaml_register_constructor(namespace=namespace)
            self.pyyaml_register_presenter(namespace=namespace)
    
        class json_encoder(json.JSONEncoder):
            def default(self, obj):
                ret = intrinsic_formatter.encode(obj)
                if type(obj)!=type(ret):
                    return ret
                return super().default(obj)
    
        @classmethod
        def dump_json_bulk(cls, obj, fp=None, skipkeys=False, ensure_ascii=True, check_circular=True, 
                           allow_nan=True, indent=None, separators=None, default=None, sort_keys=False, **kw):
    
            if fp is not None:
                return json.dump(obj, fp, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
                                 allow_nan=allow_nan, cls=cls.json_encoder, indent=indent, separators=separators,
                                 default=default, sort_keys=sort_keys, **kw)
            else:
                return json.dumps(obj, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
                                  allow_nan=allow_nan, cls=cls.json_encoder, indent=indent, separators=separators,
                                  default=default, sort_keys=sort_keys, **kw)
    
    
        def dump_json(self, obj, fp=None, skipkeys=False, ensure_ascii=False, check_circular=True, 
                      allow_nan=True, indent=4, separators=None, default=None, sort_keys=False, **kw):
            return self.dump_json_bulk(obj, fp=fp, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular, 
                                       allow_nan=allow_nan, indent=indent, separators=separators, default=default, sort_keys=sort_keys, **kw)
    
        @classmethod
        def load_json_bulk(cls, obj, parse_float=None, parse_int=None,
                           parse_constant=None, object_pairs_hook=None, namespace=globals(), **kw):
            if isinstance(obj, io.IOBase):
                return json.load(obj, object_hook=lambda x : cls.decode(x, namespace=namespace),
                                 parse_float=parse_float, parse_int=parse_int, 
                                 parse_constant=parse_constant, object_pairs_hook=object_pairs_hook, **kw)
            return json.loads(obj, object_hook=lambda x : cls.decode(x, namespace=namespace),
                              parse_float=parse_float, parse_int=parse_int,
                              parse_constant=parse_constant, object_pairs_hook=object_pairs_hook, **kw)
    
        def load_json(self, obj, parse_float=None, parse_int=None,
                      parse_constant=None, object_pairs_hook=None, namespace=globals(), **kw):
            return self.load_json_bulk(obj=obj, parse_float=parse_float, parse_int=parse_int,
                                       parse_constant=parse_constant, object_pairs_hook=object_pairs_hook,
                                       namespace=self.namespace, **kw)
    
        def dump_yaml(self, obj, stream=None, default_style=None, default_flow_style=None, encoding=None,
                      #indent=None, explicit_start=None, explicit_end=None, canonical=None,
                      indent=4, explicit_start=True, explicit_end=True, canonical=True,
                      version=None, tags=None, width=None, allow_unicode=None, line_break=None):
            return yaml.dump(obj, stream=stream, Dumper=self.pyyaml_dumper, default_style=default_style,
                             default_flow_style=default_flow_style, encoding=encoding, explicit_end=explicit_end,
                             version=version, tags=tags, canonical=canonical, indent=indent, width=width,
                             allow_unicode=allow_unicode, line_break=line_break)
    
        def load_yaml(self, obj):
            return yaml.load(obj, Loader=self.pyyaml_loader)
    
    if __name__ == '__main__':
        help(intrinsic_formatter)
                
    ########## ____INTRINSIC_FORMATTER_TEMPLATE_END____ ##########
    
    ########## ____STREAMEXTD_TEMPLATE_START____ ##########
    #
    # Show help of class when directly invoked.
    #
    if __name__ == '__main__':
        help(StreamExtd)
    
    ########## ____STREAMEXTD_TEMPLATE_END____ ##########
    
    #
    # Template data for module 
    #
    
    ########## ____BSD_3_CLAUSE_LICENSE_TEMPLATE_START____ ##########
    """
    BSD 3-Clause License
    
    Copyright (c) 2025, {____AUTHOR_NAME____}
    All rights reserved.
    
    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:
    
    1. Redistributions of source code must retain the above copyright notice, this
       list of conditions and the following disclaimer.
    
    2. Redistributions in binary form must reproduce the above copyright notice,
       this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution.
    
    3. Neither the name of the copyright holder nor the names of its
       contributors may be used to endorse or promote products derived from
       this software without specific prior written permission.
    
    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
    FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
    DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
    CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
    OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    """
    ########## ____BSD_3_CLAUSE_LICENSE_TEMPLATE_END____ ##########
    
    
    ########## ____MODULE_DIR_MAKEFILE_TEMPLATE_START____ ##########
    """
    PYTHON ?= python3
    PIP    ?= pip3
    
    MAKEFILE_DIR := $(dir $(lastword $(MAKEFILE_LIST)))
    
    MODULE_NAME  ?= {____MODULE_NAME____}
    MODULE_SPATH ?= $(subst -,_,$(MODULE_NAME))
    
    PYTMPDIR ?= $(MAKEFILE_DIR)/var/lib/python
    
    REQUIERD_MODULES = build twine
    
    TWINE ?= $(PYTMPDIR)/bin/twine
    BUILD ?= $(PYTMPDIR)/build
    TOML ?= $(PYTMPDIR)/toml
    
    MOD_TEST_DIR_SRC  ?= $(MAKEFILE_DIR)/var/tmp/test_src
    MOD_TEST_DIR_DIST ?= $(MAKEFILE_DIR)/var/tmp/test_dist
    
    MOD_DEPENDENCIES := $(shell env PYTHONPATH=$(PYTMPDIR):$(PYTHONPATH) $(PYTHON) -c "import sys,toml;[sys.stdout.write(i) for i in toml.load('pyproject.toml').get('project')['dependencies']]")
    
    MOD_VERSION := $(shell env PYTHONPATH=$(PYTMPDIR):$(PYTHONPATH) $(PYTHON) -c "import sys,toml;sys.stdout.write(toml.load('pyproject.toml').get('project')['version'])")
    
    MOD_TEST_OPT = -h
    
    PYVERSTR       ?= $(shell $(PYTHON) -c 'import sys; sys.stdout.write(".".join([str(i) for i in sys.version_info[0:3]]))')
    LOCAL_DESTDIR  ?= $(MAKEFILE_DIR)/../../lib/python/site-packages/$(PYVERSTR)
    LOCAL_BINDIR   ?= $(MAKEFILE_DIR)/../../bin/
    PYENCASE       ?= {____PIP_MODULE_NAME____}
    
    .PHONY: info clean sdist test_src test_dist test_upload upload clean distclean install_local
    
    info:
    	@echo 'Module name         : '$(MODULE_NAME)
    	@echo 'Module short path   : '$(MODULE_SPATH)
    	@echo 'Module VERSION      : '$(MOD_VERSION)
    	@echo 'Module dependencies : '$(MOD_DEPENDENCIES)
    
    $(TWINE): 
    	env PYTHONPATH=$(PYTMPDIR):$(PYTHONPATH) $(PIP) install --target $(PYTMPDIR) $(notdir $@)
    
    $(BUILD): 
    	env PYTHONPATH=$(PYTMPDIR):$(PYTHONPATH) $(PIP) install --target $(PYTMPDIR) $(notdir $@)
    
    $(TOML):
    	env PYTHONPATH=$(PYTMPDIR):$(PYTHONPATH) $(PIP) install --target $(PYTMPDIR) $(notdir $@)
    
    sdist:
    	env PYTHONPATH=$(PYTMPDIR):$(PYTHONPATH) $(PYTHON) -m build 
    
    test_src: $(MOD_TEST_DIR_SRC)
    	-env PYTHONPATH=$(MOD_TEST_DIR_SRC):$(PYTHONPATH) $(PIP) install --target $(MOD_TEST_DIR_SRC) $(notdir $(MOD_DEPENDENCIES))
    	env PYTHONPATH=$(MOD_TEST_DIR_SRC):$(PYTHONPATH) $(PIP) install --target $(MOD_TEST_DIR_SRC) $(MAKEFILE_DIR)
    	env PYTHONPATH=$(MOD_TEST_DIR_SRC):$(PYTHONPATH) $(MOD_TEST_DIR_SRC)/bin/$(MODULE_NAME) $(MOD_TEST_OPT)
    
    test_dist: $(MOD_TEST_DIR_DIST) $(MAKEFILE_DIR)/dist/$(MODULE_SPATH)-$(MOD_VERSION).tar.gz
    	-env PYTHONPATH=$(MOD_TEST_DIR_DIST):$(PYTHONPATH) $(PIP) install --target $(MOD_TEST_DIR_DIST) $(notdir $(MOD_DEPENDENCIES))
    	env PYTHONPATH=$(MOD_TEST_DIR_DIST):$(PYTHONPATH) $(PIP) install --target $(MOD_TEST_DIR_DIST) $(MAKEFILE_DIR)/dist/$(MODULE_SPATH)-$(MOD_VERSION).tar.gz
    	env PYTHONPATH=$(MOD_TEST_DIR_DIST):$(PYTHONPATH) $(MOD_TEST_DIR_DIST)/bin/$(MODULE_NAME) $(MOD_TEST_OPT)
    
    install_local: 
    	-mkdir -p $(LOCAL_DESTDIR)
    	-env PYTHONPATH=$(MOD_TEST_DIR_SRC):$(PYTHONPATH) $(PIP) install --target $(LOCAL_DESTDIR) $(notdir $(MOD_DEPENDENCIES))
    	env  PYTHONPATH=$(MOD_TEST_DIR_SRC):$(PYTHONPATH) $(PIP) install --target $(LOCAL_DESTDIR) $(MAKEFILE_DIR)
    	if [ -f $(LOCAL_BINDIR)/$(PYENCASE) ] ; then (cd $(LOCAL_BINDIR); ln -s $(PYENCASE) $(MODULE_NAME) ) ; fi
    
    $(MAKEFILE_DIR)/dist/$(MODULE_SPATH)-$(MOD_VERSION).tar.gz: sdist
    
    $(MOD_TEST_DIR_SRC):
    	mkdir -p $(MOD_TEST_DIR_SRC)
    
    $(MOD_TEST_DIR_DIST):
    	mkdir -p $(MOD_TEST_DIR_DIST)
    
    test_upload: $(TWINE) sdist
    	env PYTHONPATH=$(PYTMPDIR):$(PYTHONPATH) $(TWINE) upload --verbose --repository pypitest $(MAKEFILE_DIR)/dist/*
    
    upload: $(TWINE) sdist
    	env PYTHONPATH=$(PYTMPDIR):$(PYTHONPATH) $(TWINE) upload --verbose $(MAKEFILE_DIR)/dist/*
    
    clean: 
    	rm -rf $(MAKEFILE_DIR)/src/$(MODULE_SPATH)/*~ \
                   $(MAKEFILE_DIR)/src/$(MODULE_SPATH)/__pycache__ \
                   $(MAKEFILE_DIR)/src/$(MODULE_SPATH)/share/data/*~ \
                   $(MAKEFILE_DIR)/dist/* \
                   $(MAKEFILE_DIR)/build/* \
                   $(MAKEFILE_DIR)/var/lib/python/* \
                   $(MAKEFILE_DIR)/*~  \
                   $(MAKEFILE_DIR)/test/*~ 
    
    distclean: clean
    	rm -rf $(MAKEFILE_DIR)/$(MODULE_SPATH).egg-info \
                   $(MAKEFILE_DIR)/dist \
                   $(MAKEFILE_DIR)/build \
                   $(MAKEFILE_DIR)/lib \
                   $(MAKEFILE_DIR)/var
    """
    ########## ____MODULE_DIR_MAKEFILE_TEMPLATE_END____ ##########
    
    ########## ____MODULE_PYPROJECT_TOML_TEMPLATE_START____ ##########
    '''
    [build-system]
    requires = ["hatchling"]
    build-backend = "hatchling.build"
    
    [project]
    name = "{____MODULE_NAME____}"
    version = "0.0.1"
    description = {____MODULE_DESC_QUOTE____}
    dependencies = [{____MODULE_REQUIREMENTS____}]
    readme = "{____README_NAME____}"
    #requires-python = ">=3.9"
    
    license = {{ file = "LICENSE" }}
    #license-files = ["LICEN[CS]E*", "vendored/licenses/*.txt", "AUTHORS.md"]
    
    keywords = [{____MODULE_KEYWORDS____}]
    
    authors = [{____MODULE_AUTHOR_LIST____}]
               
    maintainers = [{____MODULE_MAINTAINERS_LIST____}]
               
    
    classifiers = [{____MODULE_CLASSIFIER_LIST____}]
    
    [project.urls]
    Homepage = {____MODULE_HOMEPAGE_URL_QUOTE____}
    
    [project.scripts]
    {____MODULE_NAME____} = "{____MODULE_SHORT_PATH____}.{____MODULE_SHORT_PATH____}:main"
    
    '''
    ########## ____MODULE_PYPROJECT_TOML_TEMPLATE_END____ ##########
    
    ########## ____MODULE_README_MD_TEMPLATE_START____ ##########
    """
    # {____MODULE_NAME____}
    
    {____MODULE_DESC____}
    
    ## Requirement
    
    - Python: tested with version 3.X
    
    ## Usage
    
    - To be written
    
    ## Author
     {____MODULE_AUTHOR_LIST_TEXT____}
    """
    ########## ____MODULE_README_MD_TEMPLATE_END____ ##########
    
    ########## ____MODULE_DOT_GITIGNORE_TEMPLATE_START____ ##########
    '''
    # Byte-compiled / optimized / DLL files
    __pycache__/
    *.py[codz]
    *$py.class
    
    # C extensions
    *.so
    
    # Distribution / packaging
    .Python
    build/
    develop-eggs/
    dist/
    downloads/
    eggs/
    .eggs/
    lib/
    lib64/
    parts/
    sdist/
    var/
    wheels/
    share/python-wheels/
    *.egg-info/
    .installed.cfg
    *.egg
    MANIFEST
    
    # Flask stuff:
    instance/
    .webassets-cache
    
    # Scrapy stuff:
    .scrapy
    
    # PyBuilder
    .pybuilder/
    target/
    
    # IPython
    profile_default/
    ipython_config.py
    
    # PyPI configuration file
    .pypirc
    
    # This module build
    !{____GIT_DUMMYFILE____}
    '''
    ########## ____MODULE_DOT_GITIGNORE_TEMPLATE_END____ ##########
    
    ########## ____MODULE_SRC_INIT_PY_TEMPLATE_START____ ##########
    #### ____py_shebang_pattern____ ####
    # -*- coding: utf-8 -*-
    
    from .____MODULE_SHORT_PATH____ import ____MODULE_CLS_NAME____
    
    __copyright__    = 'Copyright (c) ____MODULE_CREATE_YEAR____, ____AUTHOR_NAME____'
    __version__      = ____MODULE_CLS_NAME____.VERSION
    __license__      = 'BSD-3-Clause'
    __author__       = '____AUTHOR_NAME____'
    __author_email__ = '____AUTHOR_EMAIL____'
    __url__          = ____MODULE_HOMEPAGE_URL_QUOTE____
    
    __all__ = ['____MODULE_CLS_NAME____', ]
    ########## ____MODULE_SRC_INIT_PY_TEMPLATE_END____ ##########
    
    ########## ____MODULE_SRC_MODULE_NAME_PY_TEMPLATE_START____ ##########
    #### ____py_shebang_pattern____ ####
    # -*- coding: utf-8; mode: python; -*-
    """
    ____MODULE_DESC____
    """
    import json
            
    class ____MODULE_CLS_NAME____(object):
        """
        ____MODULE_CLS_NAME____
        ____MODULE_DESC____
        """
    
        VERSION = "0.0.1"
    
        def __init__(self):
            self.contents = {}  
            
        def __repr__(self):
            return json.dumps(self.contents, ensure_ascii=False, indent=4, sort_keys=True)
            
        def __str__(self):
            return json.dumps(self.contents, ensure_ascii=False, indent=4, sort_keys=True)
    
    def main():
        help(____MODULE_CLS_NAME____)
            
    if __name__ == '__main__':
        main()
    ########## ____MODULE_SRC_MODULE_NAME_PY_TEMPLATE_END____ ##########
