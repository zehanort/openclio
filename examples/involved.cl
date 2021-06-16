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
