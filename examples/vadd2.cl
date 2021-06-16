__kernel void vadd(__global int *a, __global int *b, __global int *c, uint count) {
    int i = get_global_id(0);
    if (i < count) {
        c[i] = a[i] + b[i];
        a[i] += 1;
    }
}
