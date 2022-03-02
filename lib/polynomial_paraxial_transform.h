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
      real_to_par_(2, PolynomialParaxialTransformHelper<double, D2>::number_coefficient()),
      min_x_real_(0), max_x_real_(0), min_y_real_(0), max_y_real_(0),
      min_x_pred_(0), max_x_pred_(0), min_y_pred_(0), max_y_pred_(0)
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
    double x = std::min(std::max(Paraxial_x, min_x_pred_), max_x_pred_);
    double y = std::min(std::max(Paraxial_y, min_y_pred_), max_y_pred_);
    PolynomialParaxialTransformHelper<double, D1>::polynomial_func
      (par_to_real_, x, y, Real_x, Real_y);
    if(Paraxial_x < min_x_pred_ || Paraxial_x > max_x_pred_)
      Real_x += Paraxial_x-x;
    if(Paraxial_y < min_y_pred_ || Paraxial_y > max_y_pred_)
      Real_y += Paraxial_y-y;
  }
  void paraxial_to_real(const GeoCal::AutoDerivative<double>& Paraxial_x,
			const GeoCal::AutoDerivative<double>& Paraxial_y,
			GeoCal::AutoDerivative<double>& Real_x, 
			GeoCal::AutoDerivative<double>& Real_y) const
  {
    GeoCal::AutoDerivative<double> x = Paraxial_x;
    GeoCal::AutoDerivative<double> y = Paraxial_y;
    if(Paraxial_x.value() < min_x_pred_ || Paraxial_x.value() > max_x_pred_)
      x = std::min(std::max(Paraxial_x.value(), min_x_pred_), max_x_pred_);
    if(Paraxial_y.value() < min_y_pred_ || Paraxial_y.value() > max_y_pred_)
      y = std::min(std::max(Paraxial_y.value(), min_y_pred_), max_y_pred_);
    PolynomialParaxialTransformHelper<GeoCal::AutoDerivative<double>, D1>::polynomial_func
      (par_to_real_, x, y, Real_x, Real_y);
    if(Paraxial_x.value() < min_x_pred_ || Paraxial_x.value() > max_x_pred_)
      Real_x += Paraxial_x-x;
    if(Paraxial_y.value() < min_y_pred_ || Paraxial_y.value() > max_y_pred_)
      Real_y += Paraxial_y-y;
  }
  void real_to_paraxial(double Real_x,
			double Real_y, double& Paraxial_x, 
			double& Paraxial_y) const
  {
    double x = std::min(std::max(Real_x, min_x_real_), max_x_real_);
    double y = std::min(std::max(Real_y, min_y_real_), max_y_real_);
    PolynomialParaxialTransformHelper<double, D2>::polynomial_func
      (real_to_par_, x, y, Paraxial_x, Paraxial_y);
    if(Real_x < min_x_real_ || Real_x > max_x_real_)
      Paraxial_x += Real_x-x;
    if(Real_y < min_y_real_ || Real_y > max_y_real_)
      Paraxial_y += Real_y-y;
  }
  void real_to_paraxial(const GeoCal::AutoDerivative<double>& Real_x,
			const GeoCal::AutoDerivative<double>& Real_y,
			GeoCal::AutoDerivative<double>& Paraxial_x, 
			GeoCal::AutoDerivative<double>& Paraxial_y) const
  {
    GeoCal::AutoDerivative<double> x = Real_x;
    GeoCal::AutoDerivative<double> y = Real_y;
    if(Real_x.value() < min_x_real_ || Real_x.value() > max_x_real_)
      x = std::min(std::max(Real_x.value(), min_x_real_), max_x_real_);
    if(Real_y.value() < min_y_real_ || Real_y.value() > max_y_real_)
      y = std::min(std::max(Real_y.value(), min_y_real_), max_y_real_);
    PolynomialParaxialTransformHelper<GeoCal::AutoDerivative<double>, D2>::polynomial_func
      (real_to_par_, x, y, Paraxial_x, Paraxial_y);
    if(Real_x.value() < min_x_real_ || Real_x.value() > max_x_real_)
      Paraxial_x += Real_x-x;
    if(Real_y.value() < min_y_real_ || Real_y.value() > max_y_real_)
      Paraxial_y += Real_y-y;
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

//-----------------------------------------------------------------------
/// Polynomials really extrapolate badly. This is the range of x and y
/// that we apply the polynomial over. Outside of this range we just
/// do a linear model.
//-----------------------------------------------------------------------
  
  double min_x_real() const {return min_x_real_;}
  void min_x_real(double V) { min_x_real_ = V;}
  double max_x_real() const {return max_x_real_;}
  void max_x_real(double V) { max_x_real_ = V;}
  double min_y_real() const {return min_y_real_;}
  void min_y_real(double V) { min_y_real_ = V;}
  double max_y_real() const {return max_y_real_;}
  void max_y_real(double V) { max_y_real_ = V;}
  double min_x_pred() const {return min_x_pred_;}
  void min_x_pred(double V) { min_x_pred_ = V;}
  double max_x_pred() const {return max_x_pred_;}
  void max_x_pred(double V) { max_x_pred_ = V;}
  double min_y_pred() const {return min_y_pred_;}
  void min_y_pred(double V) { min_y_pred_ = V;}
  double max_y_pred() const {return max_y_pred_;}
  void max_y_pred(double V) { max_y_pred_ = V;}
private:
  blitz::Array<double, 2>  par_to_real_, real_to_par_;
  double min_x_real_, max_x_real_, min_y_real_, max_y_real_;
  double min_x_pred_, max_x_pred_, min_y_pred_, max_y_pred_;
  friend class boost::serialization::access;
  template<class Archive>
  void serialize(Archive & ar, const unsigned int version);
};

typedef PolynomialParaxialTransform<3, 3> PolynomialParaxialTransform_3d_3d;  
typedef PolynomialParaxialTransform<5, 3> PolynomialParaxialTransform_5d_3d;  
typedef PolynomialParaxialTransform<3, 5> PolynomialParaxialTransform_3d_5d;  
typedef PolynomialParaxialTransform<5, 5> PolynomialParaxialTransform_5d_5d;  
}

BOOST_CLASS_EXPORT_KEY(Emit::PolynomialParaxialTransform_3d_3d);
BOOST_CLASS_EXPORT_KEY(Emit::PolynomialParaxialTransform_5d_3d);
BOOST_CLASS_EXPORT_KEY(Emit::PolynomialParaxialTransform_3d_5d);
BOOST_CLASS_EXPORT_KEY(Emit::PolynomialParaxialTransform_5d_5d);
#endif

  

