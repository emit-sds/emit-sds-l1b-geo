#ifndef POLYNOMIAL_PARAXIAL_TRANSFORM_H
#define POLYNOMIAL_PARAXIAL_TRANSFORM_H
#include "camera_paraxial.h"

namespace Emit {
// We can expand this as we need different degree polynomials.
template<class T, int D> struct PolynomialParaxialTransformHelper {
  static int number_coefficient();
  static void polynomial_func(const blitz::Array<double, 2>& p, const T& x,
			      const T& y, T& Xout, T& Yout);  
};

template<class T> struct PolynomialParaxialTransformHelper<T, 3> {
  static int number_coefficient() { return 10; }
  static void polynomial_func(const blitz::Array<double, 2>& p, const T& x,
			      const T& y, T& Xout, T& Yout)
    
    {
      T x2 = x * x;
      T y2 = y * y;
      T x3 = x * x2;
      T y3 = y * y2;
      // We get the order of these polynomial powers using
      // multipolyfit.
      Xout = p(0,0) + p(0,1) * x + p(0,2) * y + p(0,3)*x2 +
	p(0,4)*x*y + p(0,5)*y2 + p(0,6)*x3 +p(0,7)*x2*y +
	p(0,8)*x*y2 + p(0,9)*y3;
      Yout = p(1,0) + p(1,1) * x + p(1,2) * y + p(1,3)*x2 +
	p(1,4)*x*y + p(1,5)*y2 + p(1,6)*x3 +p(1,7)*x2*y +
	p(1,8)*x*y2 + p(1,9)*y3;
    }
};

template<class T> struct PolynomialParaxialTransformHelper<T, 5> {
  static int number_coefficient() { return 21; }
  static void polynomial_func(const blitz::Array<double, 2>& p, const T& x,
			      const T& y, T& Xout, T& Yout)
    
    {
      T x2 = x * x;
      T y2 = y * y;
      T x3 = x * x2;
      T y3 = y * y2;
      T x4 = x * x3;
      T y4 = y * y3;
      T x5 = x * x4;
      T y5 = y * y4;
      // We get the order of these polynomial powers using
      // multipolyfit.
      Xout = p(0,0) + p(0,1) * x + p(0,2) * y + p(0,3)*x2 +
	p(0,4)*x*y + p(0,5)*y2 + p(0,6)*x3 +p(0,7)*x2*y +
	p(0,8)*x*y2 + p(0,9)*y3 + p(0,10)*x4 + p(0,11)*x3*y+
	p(0,12)*x2*y2 + p(0,13)*x*y3+p(0,14)*y4+p(0,15)*x5+
	p(0,16)*x4*y+p(0,17)*x3*y2+p(0,18)*x2*y3+p(0,19)*x*y4+
	p(0,20)*y5;
      Yout = p(1,0) + p(1,1) * x + p(1,2) * y + p(1,3)*x2 +
	p(1,4)*x*y + p(1,5)*y2 + p(1,6)*x3 +p(1,7)*x2*y +
	p(1,8)*x*y2 + p(1,9)*y3 + p(1,10)*x4 + p(1,11)*x3*y+
	p(1,12)*x2*y2 + p(1,13)*x*y3+p(1,14)*y4+p(1,15)*x5+
	p(1,16)*x4*y+p(1,17)*x3*y2+p(1,18)*x2*y3+p(1,19)*x*y4+
	p(1,20)*y5;
    }
};
  
/****************************************************************//**
  A common ParaxialTransform is to just use a polynomial to model
  the data. This implements that.
*******************************************************************/
template<int D1, int D2> class PolynomialParaxialTransform: public ParaxialTransform {
public:
//-----------------------------------------------------------------------
/// We populate the transform separately, so just have a default
/// constructor.
//-----------------------------------------------------------------------
  PolynomialParaxialTransform()
    : par_to_real_(2, PolynomialParaxialTransformHelper<double, D1>::number_coefficient()),
      real_to_par_(2, PolynomialParaxialTransformHelper<double, D2>::number_coefficient())
  {}
  virtual ~PolynomialParaxialTransform() {}
  virtual void print(std::ostream& Os) const
  { Os << "PolynomialParaxialTransform\n"
       << "  par_to_real Degree: " << D1 << "\n"
       << "  real_to_par Degree: " << D2 << "\n";
  }
  void paraxial_to_real(double Paraxial_x,
			double Paraxial_y, double& Real_x, 
			double& Real_y) const
  {
    PolynomialParaxialTransformHelper<double, D1>::polynomial_func
      (par_to_real_, Paraxial_x, Paraxial_y, Real_x, Real_y);
  }
  void paraxial_to_real(const GeoCal::AutoDerivative<double>& Paraxial_x,
			const GeoCal::AutoDerivative<double>& Paraxial_y,
			GeoCal::AutoDerivative<double>& Real_x, 
			GeoCal::AutoDerivative<double>& Real_y) const
  {
    PolynomialParaxialTransformHelper<GeoCal::AutoDerivative<double>, D1>::polynomial_func
      (par_to_real_, Paraxial_x, Paraxial_y, Real_x, Real_y);
  }
  void real_to_paraxial(double Real_x,
			double Real_y, double& Paraxial_x, 
			double& Paraxial_y) const
  {
    PolynomialParaxialTransformHelper<double, D2>::polynomial_func
      (real_to_par_, Real_x, Real_y, Paraxial_x, Paraxial_y);
  }
  void real_to_paraxial(const GeoCal::AutoDerivative<double>& Real_x,
			const GeoCal::AutoDerivative<double>& Real_y,
			GeoCal::AutoDerivative<double>& Paraxial_x, 
			GeoCal::AutoDerivative<double>& Paraxial_y) const
  {
    PolynomialParaxialTransformHelper<GeoCal::AutoDerivative<double>, D2>::polynomial_func
      (real_to_par_, Real_x, Real_y, Paraxial_x, Paraxial_y);
  }

//-----------------------------------------------------------------------
/// Polynomial from paraxial to real
//-----------------------------------------------------------------------

  const blitz::Array<double, 2>& par_to_real() const
  { return par_to_real_; }
  blitz::Array<double, 2>& par_to_real()
  { return par_to_real_; }

//-----------------------------------------------------------------------
/// Polynomial from real to paraxial
//-----------------------------------------------------------------------
  const blitz::Array<double, 2>& real_to_par() const
  { return real_to_par_; }
  blitz::Array<double, 2>& real_to_par() 
  { return real_to_par_; }
private:
  blitz::Array<double, 2>  par_to_real_, real_to_par_;
  friend class boost::serialization::access;
  template<class Archive>
  void serialize(Archive & ar, const unsigned int version);
};

typedef PolynomialParaxialTransform<3, 3> PolynomialParaxialTransform_3d_3d;  
typedef PolynomialParaxialTransform<5, 5> PolynomialParaxialTransform_5d_5d;  
}

BOOST_CLASS_EXPORT_KEY(Emit::PolynomialParaxialTransform_3d_3d);
BOOST_CLASS_EXPORT_KEY(Emit::PolynomialParaxialTransform_5d_5d);
#endif

  

