"""
curve_fit_to_data.py
    A simple example using scipy curve_fit to fit data from a file.

    Requires scipy 0.8.

    The example provided is a fit of Gaussian or Lorentzian functions
    to a data file gauss.txt.

    To fit your own data, you need to change:
    (1) def func(x,*p) to return the function you are trying to fit,
    (2) the name of the data file read in by numpy.loadtxt,
    (3) the initial p0 values in the scipy.optimize.curve_fit call.

    Don't assume the software is intelligent and produce a sensible
    result not matter what. For example, your initial guess
    for the parameters does matter. (e.g. Try changing the default guess
    for the central value in this example from 1171 to 1170 and
    see what happens.)

    For information on curve_fit.py, see
    http://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html

    Copyright (c) 2011-2014 University of Toronto
    Last Modification:  28 September 2014 by David Bailey
                fixing print discrepancy pointed out by student Paolo Albanelli
    Original Version:   31 August  2011 by David Bailey
    Contact: David Bailey <dbailey@physics.utoronto.ca>
                            (http://www.physics.utoronto.ca/~dbailey)
    License: Released under the MIT License; the full terms are this license
                are appended to the end of this file, and are also available
                at http://www.opensource.org/licenses/mit-license.php.

    Note: The code is over-commented since it is is a pedagogical example for
    	students new to python and scipy.

    Thanks to Wes Watters <wwatters@wellesley.edu> (16 September 2013) for
        pointing out problem with scipy cov matrix. (See WARNING below.)

"""

import matplotlib               # http://matplotlib.sourceforge.net
# Explicitly choose normal TkAgg Backend, in case your python installation
#       does not already have a suitable choice in your matplotlibrc file.
#       This line may be deleted if the script runds without it. See
# http://matplotlib.sourceforge.net/faq/installing_faq.html#what-is-a-backend.
matplotlib.use('TKAgg')

import numpy                    # http://numpy.scipy.org/
import scipy                    # http://scipy.org/
import scipy.optimize, scipy.special, scipy.stats
from matplotlib import pyplot

## Function to fit: 'x' is the independent variable(s), 'p' the parameter vector
#   Note:   These are just examples; normally you will write your own function.
#           A one line lambda function definition  can be used for very simple
#           functions, but using "def" always works.
#   Note:   "*p" unpacks p into its elements; needed for curvefit
def gaussian(x,*p) :
    # A gaussian peak with:
    #   Constant Background          : p[0]
    #   Peak height above background : p[1]
    #   Central value                : p[2]
    #   Standard deviation           : p[3]
    return p[0]+p[1]*numpy.exp(-1*(x-p[2])**2/(2*p[3]**2))
def lorentzian(x,*p) :
    # A lorentzian peak with:
    #   Constant Background          : p[0]
    #   Peak height above background : p[1]
    #   Central value                : p[2]
    #   Full Width at Half Maximum   : p[3]
    return p[0]+(p[1]/numpy.pi)/(1.0+((x-p[2])/p[3])**2)
def linear(x,*p) :
    # A linear fit with:
    #   Intercept                    : p[0]
    #   Slope                        : p[1]
    return p[0]+p[1]*x
def power(x,*p) :
    # A power law fit with:
    #   Normalization                : p[0]
    #   Offset                       : p[1]
    #   Constant                     : p[3]
    return p[0]*(x-p[1])**p[2]+p[3]


## Choose function
func = gaussian

## Initial guesses for fit parameters
#       Note: The comma after the last paramater is unnecessary unless
#               you only have one parameter.
p_guess = (10.,40.,1171.,1,)

## Load data to fit
x_data, y_data, y_sigma = numpy.loadtxt('gauss.txt', unpack=True)
# Warning: If you have created your own data file, which looks fine
#    but produces "ValueError: too many values to unpack", then it may have
#    invisible characters or non-standard linebreaks, e.g. Mac CR instead
#    of Windows style CRLF. This may be fixed by opening the data file in
#    a text editor and resaving it with standard line breaks.

# Record initial function guess for later plotting
#   Create many finely spaced points for function plot
#           linspace(start,stop,num)
#               returns num evenly spaced samples over interval [start, stop]
x_func = numpy.linspace(min(x_data),max(x_data),150)
initial_plot = func(x_func,*p_guess)

## Fit function to data

# This fits the function "func" to the data points (x, y_data) with y
#   uncertainties "y_sigma", and initial parameter values p0.
#   Note: Try replacing 1171 by 1170 and see what happens.
try:
    p, cov = scipy.optimize.curve_fit(
                func, x_data, y_data, p0=p_guess, sigma=y_sigma,
                maxfev=100*(len(x_data)+1))
    #     Notes: maxfev is the maximum number of func evaluations tried; you
    #               can try increasing this value if the fit fails.
    #            If the program returns a good chi-squared but an infinite
    #               covariance and no parameter uncertainties, it may be
    #               because you have a redundant parameter;
    #               try fitting with a simpler function.
# Catch any fitting errors
except:
    p, cov = p_guess, None

# Calculate residuals (difference between data and fit)
for i in enumerate(y_data):
    y_fit = func(x_data,*p)
    y_residual = y_data - y_fit

# Calculate degrees of freedom of fit
dof = len(x_data) - len(p)

## Output results

print "******** RESULTS FROM FIT ******** (by curve_fit_to_data.py)"
print "Fit Function: ",func.__name__
print "\nNumber of Data Points = %7g, Number of Parameters = %1g"\
      %(len(x_data), len(p) )

print "\nCovariance Matrix : \n", cov, "\n"
try:
    # Calculate Chi-squared
    chisq = sum(((y_data-func(x_data,*p))/y_sigma)**2)
    # WARNING : Scipy seems to use non-standard poorly documented notation for cov,
    #   which misleads many people. See "cov_x" on
    #   http://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.leastsq.html#scipy.optimize.leastsq
    #   (which underlies curve_fit) and also discussion at
    #   http://stackoverflow.com/questions/14854339/in-scipy-how-and-why-does-curve-fit-calculate-the-covariance-of-the-parameter-es.
    #   I think this agrees with @cdeil at http://nbviewer.ipython.org/5014170/.
    #   THANKS to Wes Watters <wwatters@wellesley.edu> for pointing this out to me (16 September 2013)
    #
    # Convert Scipy cov matrix to standard covariance matrix.
    cov = cov*dof/chisq
    print "Correlation Matrix :"
    for i,row in enumerate(cov):
        for j in range(len(p)) :
            print "%10f"%(cov[i,j]/numpy.sqrt(cov[i,i]*cov[j,j])),
                # Note: comma at end of print statement suppresses new line
        print
    print "\nEstimated parameters and uncertainties (with initial guesses)"
#  Note: If the fit is poor, i.e. chisq/dof is large, the uncertainties
#   are scaled up. If the fit is too good, i.e. chisq/dof << 1, it suggests
#   that the uncertainties have been overestimated, but the uncertainties
#   are not scaled down.
    for i in range(len(p)) :
        print ("   p[%d] = %10.5f +/- %10.5f      (%10.5f)"
                   %(i,p[i],cov[i,i]**0.5*max(1,numpy.sqrt(chisq/dof)),
                       p_guess[i]))

    cdf = scipy.special.chdtrc(dof,chisq)
    print "\nChi-Squared/dof = %10.5f, CDF = %10.5f%%"\
        %(chisq/dof, 100.*cdf)
    if cdf < 0.05 :
        print "\nNOTE: This does not appear to be a great fit, so the"
        print "      parameter uncertainties may underestimated."
    elif cdf > 0.95 :
        print "\nNOTE: This fit seems better than expected, so the"
        print "      data uncertainties may have been overestimated."


# If cov has not been calculated because of a bad fit, the above block
#   will cause a python TypeError which is caught by this try-except structure.
except TypeError:
    print "**** BAD FIT ****"
    print "Parameters were: ",p
    # Calculate Chi-squared for current parameters
    chisq = sum(((y_data-func(x_data,*p))/y_sigma)**2)
    print "Chi-Squared/dof for these parameter values = %10.5f, CDF = %10.5f%%"\
        %(chisq/dof, 100.*float(scipy.special.chdtrc(dof,chisq)))
    print "Uncertainties not calculated."
    print
    print "Try a different initial guess for the fit parameters."
    print "Or if these parameters appear close to a good fit, try giving"
    print "    the fitting program more time by increasing the value of maxfev."
    chisq = None


## Plot

# create figure with light gray background
fig = pyplot.figure(facecolor="0.98")
# 3 rows, 1 column, subplot 1
#   3 rows are declared, but there are only 2 plots; this leaves room for text
#       in the empty 3rd row
fit = fig.add_subplot(311)
# remove tick labels from upper plot (for clean look)
fit.set_xticklabels( () )

# Plot data as red circles, and fitted function as (default) line
#   (The sort is in case the x data are not in sequential order.)
fit.plot(x_data,y_data,'ro', numpy.sort(x_data), func(numpy.sort(x_data),*p))
#   draw starting guess as dashed green line ('r-')
fit.plot(x_func, initial_plot, 'g-', label="Start", linestyle="--")
# Add error bars on data as red crosses.
fit.errorbar(x_data, y_data, yerr=y_sigma, fmt='r+')

# separate plot to show residuals
residuals = fig.add_subplot(312) # 3 rows, 1 column, subplot 2
residuals.errorbar(x_data, y_residual, yerr=y_sigma, fmt='r+', label="Residuals")
# make sure residual plot has same x axis as fit plot
residuals.set_xlim(fit.get_xlim())
residuals.axhline(y=0) # draw horizontal line at 0 on vertical axis
# Label axes
pyplot.xlabel("energy [KeV]")
pyplot.ylabel("Counts")
# These data look better if 'plain', not scientific, notation is used,
#   and if the tick labels are not offset by a constant (as is done by default).
#   Note: This only works for matplotlib version 1.0 and newer, so it is
#           enclosed in a "try" to avoid errors.
try:
    pyplot.ticklabel_format(style='plain', useOffset=False, axis='x')
except: pass

# print selected information in empty 3rd plot row
try:
    pyplot.figtext(0.05,0.25,"Converged with ChiSq = " + str(chisq) + ", DOF = " +
        str(dof) + ", CDF = " + str(100*scipy.special.chdtrc(dof,chisq))+"%")
    for i, value in enumerate(p):
    	pyplot.figtext(0.08,0.16-i*0.03, "p["+str(i)+"]" + " = " +
                   str(p[i]).ljust(18) + " +/- " +
                   str(numpy.sqrt(cov[i,i])*max(1,numpy.sqrt(chisq/dof))),
                   fontdict=None)
    	# Note: Including family="Monospace" in the above figtext call will
    	#       produce nicer looking output, but can cause problems with
    	#       some older python installations.
except TypeError:
    pyplot.figtext(0.05,0.25,"BAD FIT.  Guess again.")


# Display the plot
pyplot.show()
    # To print the plot, save it first, and then print the saved image.
    # Closing the plot window will end the python script.

##### End curve_fit_to_data

"""
Full text of MIT License:

    Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
