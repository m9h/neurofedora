/*
 * Minimal CLAPACK prototype shim for rr-libstruct on Fedora.
 *
 * rr-libstruct was written against CLAPACK (the f2c-translated LAPACK), which
 * Fedora no longer ships. The actual symbols (dgetrf_, zgeev_, ...) are the
 * standard Fortran LAPACK routines provided by Fedora's liblapack/libblas; only
 * the f2c-style prototypes are missing. This header supplies exactly the
 * prototypes rr-libstruct uses, in f2c types (integer/doublereal/doublecomplex
 * come from the system <f2c.h>, shipped by the 'f2c' package). Installed as
 * <clapack.h> so the upstream #include "clapack.h" resolves unchanged.
 */
#ifndef RR_LIBSTRUCT_CLAPACK_SHIM_H
#define RR_LIBSTRUCT_CLAPACK_SHIM_H

#include <f2c.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Subroutine */ int dgecon_(char *norm, integer *n, doublereal *a, integer *lda, doublereal *anorm, doublereal *rcond, doublereal *work, integer *iwork, integer *info);
/* Subroutine */ int dgeqp3_(integer *m, integer *n, doublereal *a, integer *lda, integer *jpvt, doublereal *tau, doublereal *work, integer *lwork, integer *info);
/* Subroutine */ int dgeqrf_(integer *m, integer *n, doublereal *a, integer *lda, doublereal *tau, doublereal *work, integer *lwork, integer *info);
/* Subroutine */ int dgesdd_(char *jobz, integer *m, integer *n, doublereal *a, integer *lda, doublereal *s, doublereal *u, integer *ldu, doublereal *vt, integer *ldvt, doublereal *work, integer *lwork, integer *iwork, integer *info);
/* Subroutine */ int dgetc2_(integer *n, doublereal *a, integer *lda, integer *ipiv, integer *jpiv, integer *info);
/* Subroutine */ int dgetrf_(integer *m, integer *n, doublereal *a, integer *lda, integer *ipiv, integer *info);
/* Subroutine */ int dgetri_(integer *n, doublereal *a, integer *lda, integer *ipiv, doublereal *work, integer *lwork, integer *info);
doublereal dlange_(char *norm, integer *m, integer *n, doublereal *a, integer *lda, doublereal *work);
/* Subroutine */ int dorgqr_(integer *m, integer *n, integer *k, doublereal *a, integer *lda, doublereal *tau, doublereal *work, integer *lwork, integer *info);
/* Subroutine */ int zgeev_(char *jobvl, char *jobvr, integer *n, doublecomplex *a, integer *lda, doublecomplex *w, doublecomplex *vl, integer *ldvl, doublecomplex *vr, integer *ldvr, doublecomplex *work, integer *lwork, doublereal *rwork, integer *info);
/* Subroutine */ int zgesdd_(char *jobz, integer *m, integer *n, doublecomplex *a, integer *lda, doublereal *s, doublecomplex *u, integer *ldu, doublecomplex *vt, integer *ldvt, doublecomplex *work, integer *lwork, doublereal *rwork, integer *iwork, integer *info);
/* Subroutine */ int zgetrf_(integer *m, integer *n, doublecomplex *a, integer *lda, integer *ipiv, integer *info);
/* Subroutine */ int zgetri_(integer *n, doublecomplex *a, integer *lda, integer *ipiv, doublecomplex *work, integer *lwork, integer *info);

#ifdef __cplusplus
}
#endif

#endif /* RR_LIBSTRUCT_CLAPACK_SHIM_H */
