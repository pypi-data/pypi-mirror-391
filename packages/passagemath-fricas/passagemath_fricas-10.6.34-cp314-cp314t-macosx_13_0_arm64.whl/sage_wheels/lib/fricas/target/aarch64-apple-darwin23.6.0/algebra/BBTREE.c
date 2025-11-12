/*      Compiler: ECL 24.5.10                                         */
/*      Date: 2025/11/11 03:27 (yyyy/mm/dd)                           */
/*      Machine: Darwin 23.6.0 arm64                                  */
/*      Source: /Users/runner/sage-local/var/tmp/sage/build/fricas-1.3.12/src/pre-generated/src/algebra/BBTREE.lsp */
#include <ecl/ecl-cmp.h>
#include "/Users/runner/sage-local/var/tmp/sage/build/fricas-1.3.12/src/_build/target/aarch64-apple-darwin23.6.0/algebra/BBTREE.eclh"
/*      function definition for BBTREE;setleaves!;%L%;1               */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L476_bbtree_setleaves___l__1_(cl_object v1_t_, cl_object v2_u_, cl_object v3_)
{
 cl_object T0, T1, T2, T3;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4_acc_;
  cl_object v5;
  cl_object v6_i_;
  cl_object v7_m_;
  cl_object v8_n_;
  v4_acc_ = ECL_NIL;
  v5 = ECL_NIL;
  v6_i_ = ECL_NIL;
  v7_m_ = ecl_make_fixnum(0);
  v8_n_ = ecl_make_fixnum(0);
  v8_n_ = ecl_make_fixnum(ecl_length(v2_u_));
  if (!((v8_n_)==(ecl_make_fixnum(0)))) { goto L9; }
  {
   cl_object v9;
   v9 = (v3_)->vector.self.t[9];
   T0 = _ecl_car(v9);
   T1 = _ecl_cdr(v9);
   if (Null((cl_env_copy->function=T0)->cfun.entry(2, v1_t_, T1))) { goto L11; }
  }
  value0 = v1_t_;
  cl_env_copy->nvalues = 1;
  return value0;
L11:;
  value0 = ecl_function_dispatch(cl_env_copy,VV[28])(1, VV[1]) /*  error */;
  return value0;
L9:;
  if (!((v8_n_)==(ecl_make_fixnum(1)))) { goto L15; }
  {
   cl_object v9;
   v9 = (v3_)->vector.self.t[10];
   T0 = _ecl_car(v9);
   if (Null(v2_u_)) { goto L21; }
   T1 = _ecl_car(v2_u_);
   goto L20;
L21:;
   T1 = ecl_function_dispatch(cl_env_copy,VV[29])(0) /*  FIRST_ERROR  */;
L20:;
   T2 = _ecl_cdr(v9);
   (cl_env_copy->function=T0)->cfun.entry(3, v1_t_, T1, T2);
  }
  value0 = v1_t_;
  cl_env_copy->nvalues = 1;
  return value0;
L15:;
  v7_m_ = ecl_function_dispatch(cl_env_copy,VV[30])(2, v8_n_, ecl_make_fixnum(2)) /*  QUOTIENT2 */;
  v4_acc_ = ECL_NIL;
  v6_i_ = ecl_make_fixnum(1);
  v5 = v7_m_;
L29:;
  if (!((ecl_fixnum(v6_i_))>(ecl_fixnum(v5)))) { goto L35; }
  goto L30;
L35:;
  if (Null(v2_u_)) { goto L41; }
  T0 = _ecl_car(v2_u_);
  goto L40;
L41:;
  T0 = ecl_function_dispatch(cl_env_copy,VV[29])(0) /*  FIRST_ERROR   */;
L40:;
  v4_acc_ = CONS(T0,v4_acc_);
  v2_u_ = _ecl_cdr(v2_u_);
  goto L37;
L37:;
  v6_i_ = ecl_make_fixnum((ecl_fixnum(v6_i_))+1);
  goto L29;
L30:;
  goto L28;
L28:;
  {
   cl_object v9;
   v9 = (v3_)->vector.self.t[13];
   T0 = _ecl_car(v9);
   {
    cl_object v10;
    v10 = (v3_)->vector.self.t[11];
    T2 = _ecl_car(v10);
    T3 = _ecl_cdr(v10);
    T1 = (cl_env_copy->function=T2)->cfun.entry(2, v1_t_, T3);
   }
   T2 = cl_nreverse(v4_acc_);
   T3 = _ecl_cdr(v9);
   (cl_env_copy->function=T0)->cfun.entry(3, T1, T2, T3);
  }
  {
   cl_object v9;
   v9 = (v3_)->vector.self.t[13];
   T0 = _ecl_car(v9);
   {
    cl_object v10;
    v10 = (v3_)->vector.self.t[14];
    T2 = _ecl_car(v10);
    T3 = _ecl_cdr(v10);
    T1 = (cl_env_copy->function=T2)->cfun.entry(2, v1_t_, T3);
   }
   T2 = _ecl_cdr(v9);
   (cl_env_copy->function=T0)->cfun.entry(3, T1, v2_u_, T2);
  }
  value0 = v1_t_;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for BBTREE;balancedBinaryTree;NniS%;2     */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L477_bbtree_balancedbinarytree_nnis__2_(cl_object v1_n_, cl_object v2_val_, cl_object v3_)
{
 cl_object T0, T1, T2, T3, T4, T5;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4_m_;
  v4_m_ = ecl_make_fixnum(0);
  if (!((v1_n_)==(ecl_make_fixnum(0)))) { goto L3; }
  {
   cl_object v5;
   v5 = (v3_)->vector.self.t[15];
   T0 = _ecl_car(v5);
   T1 = _ecl_cdr(v5);
   value0 = (cl_env_copy->function=T0)->cfun.entry(1, T1);
   return value0;
  }
L3:;
  if (!((v1_n_)==(ecl_make_fixnum(1)))) { goto L7; }
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[16];
   T0 = _ecl_car(v6);
   {
    cl_object v7;
    v7 = (v3_)->vector.self.t[15];
    T2 = _ecl_car(v7);
    T3 = _ecl_cdr(v7);
    T1 = (cl_env_copy->function=T2)->cfun.entry(1, T3);
   }
   {
    cl_object v7;
    v7 = (v3_)->vector.self.t[15];
    T3 = _ecl_car(v7);
    T4 = _ecl_cdr(v7);
    T2 = (cl_env_copy->function=T3)->cfun.entry(1, T4);
   }
   T3 = _ecl_cdr(v6);
   value0 = (cl_env_copy->function=T0)->cfun.entry(4, T1, v2_val_, T2, T3);
   return value0;
  }
L7:;
  v4_m_ = ecl_function_dispatch(cl_env_copy,VV[30])(2, v1_n_, ecl_make_fixnum(2)) /*  QUOTIENT2 */;
  {
   cl_object v7;
   v7 = (v3_)->vector.self.t[16];
   T0 = _ecl_car(v7);
   {
    cl_object v8;
    v8 = (v3_)->vector.self.t[18];
    T2 = _ecl_car(v8);
    T3 = _ecl_cdr(v8);
    T1 = (cl_env_copy->function=T2)->cfun.entry(3, v4_m_, v2_val_, T3);
   }
   {
    cl_object v8;
    v8 = (v3_)->vector.self.t[18];
    T3 = _ecl_car(v8);
    T4 = ecl_minus(v1_n_,v4_m_);
    T5 = _ecl_cdr(v8);
    T2 = (cl_env_copy->function=T3)->cfun.entry(3, T4, v2_val_, T5);
   }
   T3 = _ecl_cdr(v7);
   value0 = (cl_env_copy->function=T0)->cfun.entry(4, T1, v2_val_, T2, T3);
   return value0;
  }
 }
}
/*      function definition for BBTREE;mapUp!;%MS;3                   */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L478_bbtree_mapup___ms_3_(cl_object v1_x_, cl_object v2_fn_, cl_object v3_)
{
 cl_object T0, T1, T2, T3, T4, T5, T6, T7, T8;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4;
  v4 = (v3_)->vector.self.t[9];
  T0 = _ecl_car(v4);
  T1 = _ecl_cdr(v4);
  if (Null((cl_env_copy->function=T0)->cfun.entry(2, v1_x_, T1))) { goto L1; }
 }
 value0 = ecl_function_dispatch(cl_env_copy,VV[28])(1, VV[4]) /*  error */;
 return value0;
L1:;
 {
  cl_object v4;
  v4 = (v3_)->vector.self.t[19];
  T0 = _ecl_car(v4);
  T1 = _ecl_cdr(v4);
  if (Null((cl_env_copy->function=T0)->cfun.entry(2, v1_x_, T1))) { goto L5; }
 }
 {
  cl_object v4;
  v4 = (v3_)->vector.self.t[21];
  T0 = _ecl_car(v4);
  T1 = _ecl_cdr(v4);
  value0 = (cl_env_copy->function=T0)->cfun.entry(3, v1_x_, VV[5], T1);
  return value0;
 }
L5:;
 {
  cl_object v5;
  v5 = (v3_)->vector.self.t[28];
  T0 = _ecl_car(v5);
  T2 = _ecl_car(v2_fn_);
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[25];
   T4 = _ecl_car(v6);
   {
    cl_object v7;
    v7 = (v3_)->vector.self.t[23];
    T6 = _ecl_car(v7);
    T7 = _ecl_cdr(v7);
    T5 = (cl_env_copy->function=T6)->cfun.entry(3, v1_x_, VV[6], T7);
   }
   T6 = _ecl_cdr(v6);
   T3 = (cl_env_copy->function=T4)->cfun.entry(3, T5, v2_fn_, T6);
  }
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[25];
   T5 = _ecl_car(v6);
   {
    cl_object v7;
    v7 = (v3_)->vector.self.t[27];
    T7 = _ecl_car(v7);
    T8 = _ecl_cdr(v7);
    T6 = (cl_env_copy->function=T7)->cfun.entry(3, v1_x_, VV[7], T8);
   }
   T7 = _ecl_cdr(v6);
   T4 = (cl_env_copy->function=T5)->cfun.entry(3, T6, v2_fn_, T7);
  }
  T5 = _ecl_cdr(v2_fn_);
  T1 = (cl_env_copy->function=T2)->cfun.entry(3, T3, T4, T5);
  T2 = _ecl_cdr(v5);
  value0 = (cl_env_copy->function=T0)->cfun.entry(4, v1_x_, VV[5], T1, T2);
  return value0;
 }
}
/*      function definition for BBTREE;mapUp!;2%M%;4                  */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L479_bbtree_mapup__2_m__4_(cl_object v1_x_, cl_object v2_y_, cl_object v3_fn_, cl_object v4_)
{
 cl_object T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v5;
  v5 = (v4_)->vector.self.t[9];
  T0 = _ecl_car(v5);
  T1 = _ecl_cdr(v5);
  if (((cl_env_copy->function=T0)->cfun.entry(2, v1_x_, T1))!=ECL_NIL) { goto L4; }
 }
 {
  cl_object v5;
  v5 = (v4_)->vector.self.t[9];
  T0 = _ecl_car(v5);
  T1 = _ecl_cdr(v5);
  if (Null((cl_env_copy->function=T0)->cfun.entry(2, v2_y_, T1))) { goto L2; }
  goto L3;
 }
L4:;
L3:;
 value0 = ecl_function_dispatch(cl_env_copy,VV[28])(1, VV[9]) /*  error */;
 return value0;
L2:;
 {
  cl_object v5;
  v5 = (v4_)->vector.self.t[19];
  T0 = _ecl_car(v5);
  T1 = _ecl_cdr(v5);
  if (Null((cl_env_copy->function=T0)->cfun.entry(2, v1_x_, T1))) { goto L10; }
 }
 {
  cl_object v5;
  v5 = (v4_)->vector.self.t[19];
  T0 = _ecl_car(v5);
  T1 = _ecl_cdr(v5);
  if (Null((cl_env_copy->function=T0)->cfun.entry(2, v2_y_, T1))) { goto L14; }
 }
 value0 = v1_x_;
 cl_env_copy->nvalues = 1;
 return value0;
L14:;
 value0 = ecl_function_dispatch(cl_env_copy,VV[28])(1, VV[10]) /*  error */;
 return value0;
L10:;
 {
  cl_object v5;
  v5 = (v4_)->vector.self.t[19];
  T0 = _ecl_car(v5);
  T1 = _ecl_cdr(v5);
  if (Null((cl_env_copy->function=T0)->cfun.entry(2, v2_y_, T1))) { goto L18; }
 }
 value0 = ecl_function_dispatch(cl_env_copy,VV[28])(1, VV[10]) /*  error */;
 return value0;
L18:;
 {
  cl_object v5;
  v5 = (v4_)->vector.self.t[30];
  T0 = _ecl_car(v5);
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[23];
   T2 = _ecl_car(v6);
   T3 = _ecl_cdr(v6);
   T1 = (cl_env_copy->function=T2)->cfun.entry(3, v1_x_, VV[6], T3);
  }
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[23];
   T3 = _ecl_car(v6);
   T4 = _ecl_cdr(v6);
   T2 = (cl_env_copy->function=T3)->cfun.entry(3, v2_y_, VV[6], T4);
  }
  T3 = _ecl_cdr(v5);
  (cl_env_copy->function=T0)->cfun.entry(4, T1, T2, v3_fn_, T3);
 }
 {
  cl_object v5;
  v5 = (v4_)->vector.self.t[30];
  T0 = _ecl_car(v5);
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[27];
   T2 = _ecl_car(v6);
   T3 = _ecl_cdr(v6);
   T1 = (cl_env_copy->function=T2)->cfun.entry(3, v1_x_, VV[7], T3);
  }
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[27];
   T3 = _ecl_car(v6);
   T4 = _ecl_cdr(v6);
   T2 = (cl_env_copy->function=T3)->cfun.entry(3, v2_y_, VV[7], T4);
  }
  T3 = _ecl_cdr(v5);
  (cl_env_copy->function=T0)->cfun.entry(4, T1, T2, v3_fn_, T3);
 }
 {
  cl_object v5;
  v5 = (v4_)->vector.self.t[28];
  T0 = _ecl_car(v5);
  T2 = _ecl_car(v3_fn_);
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[21];
   T4 = _ecl_car(v6);
   {
    cl_object v7;
    v7 = (v4_)->vector.self.t[23];
    T6 = _ecl_car(v7);
    T7 = _ecl_cdr(v7);
    T5 = (cl_env_copy->function=T6)->cfun.entry(3, v1_x_, VV[6], T7);
   }
   T6 = _ecl_cdr(v6);
   T3 = (cl_env_copy->function=T4)->cfun.entry(3, T5, VV[5], T6);
  }
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[21];
   T5 = _ecl_car(v6);
   {
    cl_object v7;
    v7 = (v4_)->vector.self.t[27];
    T7 = _ecl_car(v7);
    T8 = _ecl_cdr(v7);
    T6 = (cl_env_copy->function=T7)->cfun.entry(3, v1_x_, VV[7], T8);
   }
   T7 = _ecl_cdr(v6);
   T4 = (cl_env_copy->function=T5)->cfun.entry(3, T6, VV[5], T7);
  }
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[21];
   T6 = _ecl_car(v6);
   {
    cl_object v7;
    v7 = (v4_)->vector.self.t[23];
    T8 = _ecl_car(v7);
    T9 = _ecl_cdr(v7);
    T7 = (cl_env_copy->function=T8)->cfun.entry(3, v2_y_, VV[6], T9);
   }
   T8 = _ecl_cdr(v6);
   T5 = (cl_env_copy->function=T6)->cfun.entry(3, T7, VV[5], T8);
  }
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[21];
   T7 = _ecl_car(v6);
   {
    cl_object v7;
    v7 = (v4_)->vector.self.t[27];
    T9 = _ecl_car(v7);
    T10 = _ecl_cdr(v7);
    T8 = (cl_env_copy->function=T9)->cfun.entry(3, v2_y_, VV[7], T10);
   }
   T9 = _ecl_cdr(v6);
   T6 = (cl_env_copy->function=T7)->cfun.entry(3, T8, VV[5], T9);
  }
  T7 = _ecl_cdr(v3_fn_);
  T1 = (cl_env_copy->function=T2)->cfun.entry(5, T3, T4, T5, T6, T7);
  T2 = _ecl_cdr(v5);
  (cl_env_copy->function=T0)->cfun.entry(4, v1_x_, VV[5], T1, T2);
 }
 value0 = v1_x_;
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for BBTREE;mapDown!;%SM%;5                */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L480_bbtree_mapdown___sm__5_(cl_object v1_x_, cl_object v2_p_, cl_object v3_fn_, cl_object v4_)
{
 cl_object T0, T1, T2, T3, T4, T5;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v5;
  v5 = (v4_)->vector.self.t[9];
  T0 = _ecl_car(v5);
  T1 = _ecl_cdr(v5);
  if (Null((cl_env_copy->function=T0)->cfun.entry(2, v1_x_, T1))) { goto L2; }
 }
 value0 = v1_x_;
 cl_env_copy->nvalues = 1;
 return value0;
L2:;
 {
  cl_object v5;
  v5 = (v4_)->vector.self.t[28];
  T0 = _ecl_car(v5);
  T2 = _ecl_car(v3_fn_);
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[21];
   T4 = _ecl_car(v6);
   T5 = _ecl_cdr(v6);
   T3 = (cl_env_copy->function=T4)->cfun.entry(3, v1_x_, VV[5], T5);
  }
  T4 = _ecl_cdr(v3_fn_);
  T1 = (cl_env_copy->function=T2)->cfun.entry(3, v2_p_, T3, T4);
  T2 = _ecl_cdr(v5);
  (cl_env_copy->function=T0)->cfun.entry(4, v1_x_, VV[5], T1, T2);
 }
 {
  cl_object v5;
  v5 = (v4_)->vector.self.t[31];
  T0 = _ecl_car(v5);
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[23];
   T2 = _ecl_car(v6);
   T3 = _ecl_cdr(v6);
   T1 = (cl_env_copy->function=T2)->cfun.entry(3, v1_x_, VV[6], T3);
  }
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[21];
   T3 = _ecl_car(v6);
   T4 = _ecl_cdr(v6);
   T2 = (cl_env_copy->function=T3)->cfun.entry(3, v1_x_, VV[5], T4);
  }
  T3 = _ecl_cdr(v5);
  (cl_env_copy->function=T0)->cfun.entry(4, T1, T2, v3_fn_, T3);
 }
 {
  cl_object v5;
  v5 = (v4_)->vector.self.t[31];
  T0 = _ecl_car(v5);
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[27];
   T2 = _ecl_car(v6);
   T3 = _ecl_cdr(v6);
   T1 = (cl_env_copy->function=T2)->cfun.entry(3, v1_x_, VV[7], T3);
  }
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[21];
   T3 = _ecl_car(v6);
   T4 = _ecl_cdr(v6);
   T2 = (cl_env_copy->function=T3)->cfun.entry(3, v1_x_, VV[5], T4);
  }
  T3 = _ecl_cdr(v5);
  (cl_env_copy->function=T0)->cfun.entry(4, T1, T2, v3_fn_, T3);
 }
 value0 = v1_x_;
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for BBTREE;mapDown!;%SM%;6                */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L481_bbtree_mapdown___sm__6_(cl_object v1_x_, cl_object v2_p_, cl_object v3_fn_, cl_object v4_)
{
 cl_object T0, T1, T2, T3, T4, T5, T6;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v5_u_;
  v5_u_ = ECL_NIL;
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[9];
   T0 = _ecl_car(v6);
   T1 = _ecl_cdr(v6);
   if (Null((cl_env_copy->function=T0)->cfun.entry(2, v1_x_, T1))) { goto L3; }
  }
  value0 = v1_x_;
  cl_env_copy->nvalues = 1;
  return value0;
L3:;
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[28];
   T0 = _ecl_car(v6);
   T1 = _ecl_cdr(v6);
   (cl_env_copy->function=T0)->cfun.entry(4, v1_x_, VV[5], v2_p_, T1);
  }
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[19];
   T0 = _ecl_car(v6);
   T1 = _ecl_cdr(v6);
   if (Null((cl_env_copy->function=T0)->cfun.entry(2, v1_x_, T1))) { goto L11; }
  }
  value0 = v1_x_;
  cl_env_copy->nvalues = 1;
  return value0;
L11:;
  T0 = _ecl_car(v3_fn_);
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[21];
   T2 = _ecl_car(v6);
   {
    cl_object v7;
    v7 = (v4_)->vector.self.t[23];
    T4 = _ecl_car(v7);
    T5 = _ecl_cdr(v7);
    T3 = (cl_env_copy->function=T4)->cfun.entry(3, v1_x_, VV[6], T5);
   }
   T4 = _ecl_cdr(v6);
   T1 = (cl_env_copy->function=T2)->cfun.entry(3, T3, VV[5], T4);
  }
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[21];
   T3 = _ecl_car(v6);
   {
    cl_object v7;
    v7 = (v4_)->vector.self.t[27];
    T5 = _ecl_car(v7);
    T6 = _ecl_cdr(v7);
    T4 = (cl_env_copy->function=T5)->cfun.entry(3, v1_x_, VV[7], T6);
   }
   T5 = _ecl_cdr(v6);
   T2 = (cl_env_copy->function=T3)->cfun.entry(3, T4, VV[5], T5);
  }
  T3 = _ecl_cdr(v3_fn_);
  v5_u_ = (cl_env_copy->function=T0)->cfun.entry(4, T1, T2, v2_p_, T3);
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[35];
   T0 = _ecl_car(v6);
   {
    cl_object v7;
    v7 = (v4_)->vector.self.t[23];
    T2 = _ecl_car(v7);
    T3 = _ecl_cdr(v7);
    T1 = (cl_env_copy->function=T2)->cfun.entry(3, v1_x_, VV[6], T3);
   }
   {
    cl_object v7;
    v7 = (v4_)->vector.self.t[33];
    T3 = _ecl_car(v7);
    T4 = _ecl_cdr(v7);
    T2 = (cl_env_copy->function=T3)->cfun.entry(3, v5_u_, ecl_make_fixnum(1), T4);
   }
   T3 = _ecl_cdr(v6);
   (cl_env_copy->function=T0)->cfun.entry(4, T1, T2, v3_fn_, T3);
  }
  {
   cl_object v6;
   v6 = (v4_)->vector.self.t[35];
   T0 = _ecl_car(v6);
   {
    cl_object v7;
    v7 = (v4_)->vector.self.t[27];
    T2 = _ecl_car(v7);
    T3 = _ecl_cdr(v7);
    T1 = (cl_env_copy->function=T2)->cfun.entry(3, v1_x_, VV[7], T3);
   }
   {
    cl_object v7;
    v7 = (v4_)->vector.self.t[33];
    T3 = _ecl_car(v7);
    T4 = _ecl_cdr(v7);
    T2 = (cl_env_copy->function=T3)->cfun.entry(3, v5_u_, ecl_make_fixnum(2), T4);
   }
   T3 = _ecl_cdr(v6);
   (cl_env_copy->function=T0)->cfun.entry(4, T1, T2, v3_fn_, T3);
  }
  value0 = v1_x_;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for BalancedBinaryTree;                   */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L482_balancedbinarytree__(cl_object v1__1_)
{
 cl_object T0, T1, T2, T3, T4, T5, T6;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v2_pv__;
  cl_object v3;
  cl_object v4;
  cl_object v5;
  cl_object v6_;
  cl_object v7_dv__;
  cl_object v8dv_1;
  v2_pv__ = ECL_NIL;
  v3 = ECL_NIL;
  v4 = ECL_NIL;
  v5 = ECL_NIL;
  v6_ = ECL_NIL;
  v7_dv__ = ECL_NIL;
  v8dv_1 = ECL_NIL;
  v8dv_1 = ecl_function_dispatch(cl_env_copy,VV[37])(1, v1__1_) /*  devaluate */;
  v7_dv__ = cl_list(2, VV[14], v8dv_1);
  v6_ = ecl_function_dispatch(cl_env_copy,VV[38])(1, ecl_make_fixnum(49)) /*  GETREFV */;
  (v6_)->vector.self.t[0]= v7_dv__;
  v5 = ecl_function_dispatch(cl_env_copy,VV[39])(2, v1__1_, VV[15]) /*  HasCategory */;
  T1 = ecl_function_dispatch(cl_env_copy,VV[37])(1, v1__1_) /*  devaluate */;
  T2 = cl_list(2, VV[16], T1);
  if (Null(ecl_function_dispatch(cl_env_copy,VV[39])(2, v1__1_, T2) /*  HasCategory */)) { goto L20; }
  T0 = v5;
  goto L18;
L20:;
  T0 = ECL_NIL;
  goto L18;
L18:;
  T1 = ecl_function_dispatch(cl_env_copy,VV[39])(2, v1__1_, VV[17]) /*  HasCategory */;
  T2 = ecl_function_dispatch(cl_env_copy,VV[39])(2, v1__1_, VV[18]) /*  HasCategory */;
  v4 = ecl_function_dispatch(cl_env_copy,VV[39])(2, v1__1_, VV[19]) /*  HasCategory */;
  value0 = v4;
  if ((value0)!=ECL_NIL) { goto L25; }
  value0 = ecl_function_dispatch(cl_env_copy,VV[39])(2, v1__1_, VV[17]) /*  HasCategory */;
  if ((value0)!=ECL_NIL) { goto L25; }
  T3 = v5;
  goto L23;
L25:;
  T3 = value0;
  goto L23;
L23:;
  v3 = ecl_function_dispatch(cl_env_copy,VV[39])(2, v1__1_, VV[20]) /*  HasCategory */;
  value0 = v3;
  if ((value0)!=ECL_NIL) { goto L31; }
  T5 = ecl_function_dispatch(cl_env_copy,VV[37])(1, v1__1_) /*  devaluate */;
  T6 = cl_list(2, VV[16], T5);
  if (Null(ecl_function_dispatch(cl_env_copy,VV[39])(2, v1__1_, T6) /*  HasCategory */)) { goto L34; }
  T4 = v5;
  goto L29;
L34:;
  T4 = ECL_NIL;
  goto L29;
L31:;
  T4 = value0;
  goto L29;
L29:;
  T5 = cl_list(8, v5, T0, T1, T2, v4, T3, v3, T4);
  v2_pv__ = ecl_function_dispatch(cl_env_copy,VV[40])(3, ecl_make_fixnum(0), ecl_make_fixnum(0), T5) /*  buildPredVector */;
  (v6_)->vector.self.t[3]= v2_pv__;
  T0 = ecl_list1(v8dv_1);
  T1 = CONS(ecl_make_fixnum(1),v6_);
  ecl_function_dispatch(cl_env_copy,VV[41])(4, ECL_SYM_VAL(cl_env_copy,VV[21]), VV[14], T0, T1) /*  haddProp */;
  ecl_function_dispatch(cl_env_copy,VV[42])(1, v6_) /*  stuffDomainSlots */;
  (v6_)->vector.self.t[6]= v1__1_;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[39])(2, v6_, VV[22]) /*  HasCategory */)) { goto L41; }
  ecl_function_dispatch(cl_env_copy,VV[43])(2, v6_, ecl_make_fixnum(256)) /*  augmentPredVector */;
  goto L39;
L41:;
  goto L39;
L39:;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[39])(2, v1__1_, VV[18]) /*  HasCategory */)) { goto L45; }
  if (Null(ecl_function_dispatch(cl_env_copy,VV[39])(2, v6_, VV[22]) /*  HasCategory */)) { goto L45; }
  ecl_function_dispatch(cl_env_copy,VV[43])(2, v6_, ecl_make_fixnum(512)) /*  augmentPredVector */;
  goto L43;
L45:;
  goto L43;
L43:;
  if (Null(v4)) { goto L50; }
  if (Null(ecl_function_dispatch(cl_env_copy,VV[39])(2, v6_, VV[22]) /*  HasCategory */)) { goto L50; }
  ecl_function_dispatch(cl_env_copy,VV[43])(2, v6_, ecl_make_fixnum(1024)) /*  augmentPredVector */;
  goto L48;
L50:;
  goto L48;
L48:;
  if (Null(ecl_function_dispatch(cl_env_copy,VV[39])(2, v6_, VV[23]) /*  HasCategory */)) { goto L55; }
  ecl_function_dispatch(cl_env_copy,VV[43])(2, v6_, ecl_make_fixnum(2048)) /*  augmentPredVector */;
  goto L53;
L55:;
  goto L53;
L53:;
  if (Null(v4)) { goto L64; }
  if ((ecl_function_dispatch(cl_env_copy,VV[39])(2, v6_, VV[22]) /*  HasCategory */)!=ECL_NIL) { goto L61; }
  goto L62;
L64:;
  goto L62;
L62:;
  if ((ecl_function_dispatch(cl_env_copy,VV[39])(2, v1__1_, VV[17]) /*  HasCategory */)!=ECL_NIL) { goto L61; }
  if (Null(v5)) { goto L59; }
  goto L60;
L61:;
L60:;
  ecl_function_dispatch(cl_env_copy,VV[43])(2, v6_, ecl_make_fixnum(4096)) /*  augmentPredVector */;
  goto L57;
L59:;
  goto L57;
L57:;
  v2_pv__ = (v6_)->vector.self.t[3];
  T0 = ecl_function_dispatch(cl_env_copy,VV[44])(1, v1__1_) /*  BinaryTree */;
  (v6_)->vector.self.t[7]= T0;
  value0 = v6_;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for BalancedBinaryTree                    */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L483_balancedbinarytree_(cl_object volatile v1)
{
 cl_object T0, T1, T2;
 cl_object volatile env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object volatile value0;
TTL:
 {
  volatile cl_object v2;
  v2 = ECL_NIL;
  T0 = ecl_function_dispatch(cl_env_copy,VV[37])(1, v1) /*  devaluate */;
  T1 = ecl_list1(T0);
  T2 = ecl_gethash_safe(VV[14],ECL_SYM_VAL(cl_env_copy,VV[21]),ECL_NIL);
  v2 = ecl_function_dispatch(cl_env_copy,VV[46])(3, T1, T2, VV[24]) /*  lassocShiftWithFunction */;
  if (Null(v2)) { goto L3; }
  value0 = ecl_function_dispatch(cl_env_copy,VV[47])(1, v2) /*  CDRwithIncrement */;
  return value0;
L3:;
  {
   volatile bool unwinding = FALSE;
   cl_index v3=ECL_STACK_INDEX(cl_env_copy),v4;
   ecl_frame_ptr next_fr;
   ecl_frs_push(cl_env_copy,ECL_PROTECT_TAG);
   if (__ecl_frs_push_result) {
     unwinding = TRUE; next_fr=cl_env_copy->nlj_fr;
   } else {
   {
    cl_object v5;
    v5 = ecl_function_dispatch(cl_env_copy,VV[13])(1, v1) /*  BalancedBinaryTree; */;
    v2 = ECL_T;
    cl_env_copy->values[0] = v5;
    cl_env_copy->nvalues = 1;
   }
   }
   ecl_frs_pop(cl_env_copy);
   v4=ecl_stack_push_values(cl_env_copy);
   if ((v2)!=ECL_NIL) { goto L10; }
   cl_remhash(VV[14], ECL_SYM_VAL(cl_env_copy,VV[21]));
L10:;
   ecl_stack_pop_values(cl_env_copy,v4);
   if (unwinding) ecl_unwind(cl_env_copy,next_fr);
   ECL_STACK_SET_INDEX(cl_env_copy,v3);
   return cl_env_copy->values[0];
  }
 }
}