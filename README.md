# `openclio`

![PyPI](https://img.shields.io/pypi/v/openclio?color=dark%20green&label=PyPI%20release)

A tool to quickly figure out the input and output arguments of an OpenCL kernel.

## 1. What is `openclio`?

In many engineering and predictive tasks involving OpenCL kernels, it is unfortunately common that the engineer can access only the OpenCL kernel files of interest, without respective hostcodes and/or input data. In such cases, it is impossible to achieve an accurate analysis of the behavior of the kernels without spending time to actually read the kernel code and understand which arguments are used as inputs and/or outputs. This information is vital, as:

1. it impacts the transfer time of data between the CPU and the OpenCL device and, therefore, its accurate prediction,
2. its lack impedes the rapid development of testing hostcode in order to proceed to dynamic analysis and experiments,
3. it is crucial to understand what type of data we need in order to use the kernel and what type of output(s) we should expect.

Well, you should fear no more! `openclio` (*"Open Clio"* - OpenCL Input/Output) is a pure Python 3 tool created to address exactly this problem. Through a lightweight static analysis of the kernel file or the LLVM IR produced after compiling it, `openclio` classifies each argument as **input only**, **output only** or **input/output**.

## 2. Installation

To install `openclio` you only need Python 3 (3.6 or greater). Just pip it and you are good to go:

```
$ pip install openclio
```

## 3. Usage & Examples

To use `openclio` to classify the arguments of an OpenCL kernel, one can either use the kernel file of interest directly or an LLVM IR version of it (i.e., the intermediate representation used by OpenCL). For the latter, make sure that the LLVM IR file has been produced in a way similar to the following:

```
$ clang -c -x cl -emit-llvm -S -cl-std=CL2.0 -Xclang -finclude-default-header -fno-discard-value-names examples/vadd1.cl -o examples/vadd1.ll
```

**IMPORTANT NOTE 1**: Whatever you do to compile your kernel to LLVM IR, **make sure to keep the initial argument names**. In the example above, `clang` would have discarded and replaced them with other identifiers of its liking had we not used the `-fno-discard-value-names` flag!

**IMPORTANT NOTE 2**: If you intend to use `openclio` with kernel files directly, make sure that `clang` (i.e., the default compiler of the LLVM ecosystem) is installed on your machine and is visible as `clang` from your command line.

We are now ready to see `openclio` in action!

### 3.1 As a CLI utility

Let's use `openclio` on this ["hello-world" kernel](examples/vadd1.cl) (a simple vector addition):

```opencl
__kernel void vadd(__global int *a, __global int *b, __global int *c, uint count) {
    int i = get_global_id(0);
    if (i < count)
        c[i] = a[i] + b[i];
}
```

You can use `openclio` from the command line as such:

```
$ openclio -f examples/vadd1.cl -k vadd
I/O role of the arguments of OpenCL kernel examples/vadd1.cl:vadd
╒════════════╤════════╤════════╤═════════╤══════════╕
│   Position │  Name  │  Type  │  Input  │  Output  │
╞════════════╪════════╪════════╪═════════╪══════════╡
│          1 │   a    │  i32*  │    X    │          │
├────────────┼────────┼────────┼─────────┼──────────┤
│          2 │   b    │  i32*  │    X    │          │
├────────────┼────────┼────────┼─────────┼──────────┤
│          3 │   c    │  i32*  │         │    X     │
├────────────┼────────┼────────┼─────────┼──────────┤
│          4 │ count  │  i32   │    X    │          │
╘════════════╧════════╧════════╧═════════╧══════════╛
```

You can see that `openclio` figures out that `c` is the only argument that is written to, and therefore considers it to be the kernel output. But what if we also write to one of the first 2 arguments, say `a`? Check [vadd2](examples/vadd2.cl) for example:

```opencl
__kernel void vadd(__global int *a, __global int *b, __global int *c, uint count) {
    int i = get_global_id(0);
    if (i < count) {
        c[i] = a[i] + b[i];
        a[i] += 1;
    }
}
```

After compiling it and feeding the LLVM IR to `openclio`, we see that it figured out that argument `a` is used simultaneously as input and output:

```
$ openclio -f examples/vadd2.cl -k vadd
I/O role of the arguments of OpenCL kernel examples/vadd2.cl:vadd
╒════════════╤════════╤════════╤═════════╤══════════╕
│   Position │  Name  │  Type  │  Input  │  Output  │
╞════════════╪════════╪════════╪═════════╪══════════╡
│          1 │   a    │  i32*  │    X    │    X     │
├────────────┼────────┼────────┼─────────┼──────────┤
│          2 │   b    │  i32*  │    X    │          │
├────────────┼────────┼────────┼─────────┼──────────┤
│          3 │   c    │  i32*  │         │    X     │
├────────────┼────────┼────────┼─────────┼──────────┤
│          4 │ count  │  i32   │    X    │          │
╘════════════╧════════╧════════╧═════════╧══════════╛
```

Let's visit a slightly more [involved](examples/involved.cl) example:

```opencl
__kernel void involved(const __global int* a, const __global int* b, const __global int* c, __global char* d, __global char* e, __global char* f, __global int* g, const int h) {
  int i = get_global_id(0);
  if (i < h && d[i]) {
    d[i] = false;
    for (int j = a[i]; j < (b[i] + a[i]); j++) {
      int k = c[j];
      if (!f[k]) {
        g[k] = g[i] + 1;
        e[k] = true;
      }
    }
  }
}
```

If you carefully study the output of `openclio` you will realize that all arguments have been correctly classified:

```
$ openclio -f examples/involved.cl -k involved
I/O role of the arguments of OpenCL kernel examples/involved.cl:involved
╒════════════╤════════╤════════╤═════════╤══════════╕
│   Position │  Name  │  Type  │  Input  │  Output  │
╞════════════╪════════╪════════╪═════════╪══════════╡
│          1 │   a    │  i32*  │    X    │          │
├────────────┼────────┼────────┼─────────┼──────────┤
│          2 │   b    │  i32*  │    X    │          │
├────────────┼────────┼────────┼─────────┼──────────┤
│          3 │   c    │  i32*  │    X    │          │
├────────────┼────────┼────────┼─────────┼──────────┤
│          4 │   d    │  i8*   │    X    │    X     │
├────────────┼────────┼────────┼─────────┼──────────┤
│          5 │   e    │  i8*   │         │    X     │
├────────────┼────────┼────────┼─────────┼──────────┤
│          6 │   f    │  i8*   │    X    │          │
├────────────┼────────┼────────┼─────────┼──────────┤
│          7 │   g    │  i32*  │    X    │    X     │
├────────────┼────────┼────────┼─────────┼──────────┤
│          8 │   h    │  i32   │    X    │          │
╘════════════╧════════╧════════╧═════════╧══════════╛
```

What's more, `openclio` is able to figure out the I/O role of an argument even if it has been casted, i.e. "renamed" via a pointer! Take a look at the [casts](examples/casts.cl) example:

```opencl
__kernel void casts(__global double* a, __global double* b, int c, int d, int e) {
  int f, g, h, i;

  h = get_global_id(2) + 1;
  g = get_global_id(1) + 1;
  f = get_global_id(0) + 1;
  if (h > e || g > d || f > c)
    return;

  __global double(*j)[(12 / 2 * 2) + 1][(12 / 2 * 2) + 1][5] = (__global double(*)[(12 / 2 * 2) + 1][(12 / 2 * 2) + 1][5])a;
  __global double(*k)[(12 / 2 * 2) + 1][(12 / 2 * 2) + 1][5] = (__global double(*)[(12 / 2 * 2) + 1][(12 / 2 * 2) + 1][5])b;

  for (i = 0; i < 5; i++) {
    j[h][g][f][i] = j[h][g][f][i] + k[h][g][f][i];
  }
}
```

Here, arguments `a` and `b` have been casted to 2 new local variables. Again, `openclio` manages to correctly detect that `a` is the kernel's sole output, while also being used as input:

```
$ openclio -f examples/casts.cl -k casts
I/O role of the arguments of OpenCL kernel examples/casts.cl:casts
╒════════════╤════════╤═════════╤═════════╤══════════╕
│   Position │  Name  │  Type   │  Input  │  Output  │
╞════════════╪════════╪═════════╪═════════╪══════════╡
│          1 │   a    │ double* │    X    │    X     │
├────────────┼────────┼─────────┼─────────┼──────────┤
│          2 │   b    │ double* │    X    │          │
├────────────┼────────┼─────────┼─────────┼──────────┤
│          3 │   c    │   i32   │    X    │          │
├────────────┼────────┼─────────┼─────────┼──────────┤
│          4 │   d    │   i32   │    X    │          │
├────────────┼────────┼─────────┼─────────┼──────────┤
│          5 │   e    │   i32   │    X    │          │
╘════════════╧════════╧═════════╧═════════╧══════════╛
```

Lastly, `openclio` exposes a `--tablefmt` flag that controls the layout of the output table and is nothing more that the [tabulate](https://pypi.org/project/tabulate/) argument of the same name (default: `fancy_grid`), as well as a `--csv` flag that outputs the results in CSV instead of table format (and obviously overrides the `--tablefmt` flag).

### 3.2 As a Python module

`openclio` can also be used as a Python module, exposing all of its CLI functionality via the `argsIOrole` function:

```Python console
>>> from openclio import argsIOrole
>>> from pprint import pprint
>>>
>>> with open('examples/involved.ll', 'r') as f:
...     source = f.read()
...
>>> args_IO_role = argsIOrole('involved', source)  # 1st argument is the kernel name
>>> type(args_IO_role)
<class 'dict'>
>>>
>>> pprint(args_IO_role)
{'i32 %h': 'input',
 'i32* %a': 'input',
 'i32* %b': 'input',
 'i32* %c': 'input',
 'i32* %g': 'input/output',
 'i8* %d': 'input/output',
 'i8* %e': 'output',
 'i8* %f': 'input'}
>>>
```
