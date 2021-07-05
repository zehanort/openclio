import llvmlite.binding as llvm

def argsIOrole(kernelname, source, filename=None, arglist=False):

    try:
        m = llvm.parse_assembly(source)
    except RuntimeError: # it is source code, not LLVM IR

        if filename is None:
            raise ValueError('The filename argument must not be None if source code (and not LLVM IR) is provided')

        import tempfile
        import subprocess as sp

        llvmIRfile = tempfile.NamedTemporaryFile('r+')
        outs = sp.run(
            f'clang -c -x cl -emit-llvm -S -cl-std=CL2.0 -Xclang -finclude-default-header -fno-discard-value-names {filename} -o {llvmIRfile.name}'.split(),
            stdout=sp.PIPE, stderr=sp.PIPE
        )

        if outs.stderr != b'':
            raise RuntimeError('Compilation of the provided source file failed:\n' + outs.stderr.decode('ascii'))

        with open(llvmIRfile.name, 'r') as f:
            m = llvm.parse_assembly(f.read())

    try:
        f = m.get_function(kernelname)
    except NameError:
        raise NameError(f'The provided LLVM IR does not include a kernel named `{kernelname}`')

    assert f.module is m
    assert f.function is None
    assert f.block is None
    assert f.is_function and not (f.is_block or f.is_instruction)

    # step 1: if argument is "readonly", it is input
    iorole = dict(
        [
            (
                str(a),
                'input' if b'readonly' in a.attributes or not a.type.is_pointer else 'output'
            )
            for a in f.arguments
        ]
    )

    # step 2: for the rest, we must find if the kernel is reading from them (i.e., global load)
    # if yes, they are input/output, otherwise they are only output
    loads = []
    for b in f.blocks:
        for i in b.instructions:
            if i.opcode == 'load':
                loads.append(i)

    for load in loads:

        loadfrom = list(load.operands)[0]
        bufferidx = loadfrom.name

        for b in f.blocks:
            for i in b.instructions:
                if i.name == bufferidx:
                    gep = i

        if gep.opcode != 'getelementptr':
            # it is not a buffer write, not interested
            continue

        buffer = str(list(gep.operands)[0])

        # is the buffer a bitcast? (i.e. a "renaming" of the kernel argument via a pointer)
        while 'bitcast' in buffer:
            buffer = buffer.split('bitcast ')[1].split(' to')[0]
            for b in f.blocks:
                for i in b.instructions:
                    if i.name == buffer:
                        buffer = i

        if buffer in iorole.keys() and iorole[buffer] == 'output':
            iorole[buffer] = 'input/output'

    if arglist:
        return iorole, [str(a) for a in f.arguments]
    return iorole
