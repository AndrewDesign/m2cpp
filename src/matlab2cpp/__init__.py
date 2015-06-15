#!/usr/bin/env python

import supplement
import utils

import os
import imp

from treebuilder import Treebuilder
from supplement import set_variables, get_variables, str_variables
from utils import translate, qtranslate, qsupplement, build


def main(args):

    path = os.path.abspath(args.filename)
    dirname = os.path.dirname(path) + os.path.sep
    os.chdir(dirname)

    if args.disp:
        print "building tree..."

    builder = Treebuilder(dirname, disp=args.disp, comments=args.comments)

    filenames = [os.path.basename(path)]

    stack = []
    while filenames:

        filename = filenames.pop(0)
        if filename in stack:
            continue

        if args.disp:
            print "loading", filename

        stack.append(filename)

        unassigned = builder.load(filename)
        for i in xrange(len(unassigned)-1, -1, -1):

            if os.path.isfile(unassigned[i] + ".m"):
                unassigned[i] = unassigned[i] + ".m"

            if not os.path.isfile(unassigned[i]):
                # TODO error for unassigned
                del unassigned[i]

        filenames.extend(unassigned)

        if os.path.isfile(filename + ".py") and not args.reset:

            cfg = imp.load_source("cfg", filename + ".py")
            scope = cfg.scope

            types, suggestions = get_variables(builder.project[-1])
            for name in types.keys():
                if name in scope:
                    for key in scope[name].keys():
                        types[name][key] = scope[name][key]
            set_variables(builder.project[-1], types)

    if args.disp:
        print "configure tree"

    builder.configure(suggest=2*args.suggest)

    if args.disp:
        print builder.project.summary()
        print "generate translation"

    for program in builder.project[2:]:
        program.translate_tree(args)
    builder.project[0].translate_tree(args)
    builder.project[1].translate_tree(args)

    filename = builder.project[2].name

    library = str(builder.project[0])
    if library:

        if args.disp:
            print "creating library..."

        f = open(filename + ".h", "w")
        f.write(library)
        f.close()

    elif args.reset and os.path.isfile(filename+".h"):
        os.remove(filename+".h")

    errors = str(builder.project[1])
    if errors:

        if args.disp:
            print "creating error-log..."

        f = open(filename + ".log", "w")
        f.write(errors)
        f.close()

    elif args.reset and os.path.isfile(filename+".log"):
        os.remove(filename+".log")


    first = True
    for program in builder.project[2:]:

        types, suggestions = supplement.get_variables(program)
        program["str"] = program["str"].replace("__percent__", "%")

        annotation = supplement.str_variables(types, suggestions)

        filename = program.name
        f = open(filename + ".py", "w")
        f.write(annotation)
        f.close()

        if args.disp:
            print "writing translation..."

        f = open(filename + ".cpp", "w")
        f.write(str(program))
        f.close()

        if os.path.isfile(filename+".pyc"):
            os.remove(filename+".pyc")

        if first:

            first = False

            if args.tree:
                print utils.node_summary(builder.project, args)
            elif args.line:
                nodes = utils.flatten(program, False, False, False)
                for node_ in nodes:
                    if node_.line == args.line and node_.cls != "Block":
                        print node_["str"]
                        break
            else:
                print program["str"]

