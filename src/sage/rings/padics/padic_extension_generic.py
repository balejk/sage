"""
p-Adic Extension Generic

A common superclass for all extensions of Qp and Zp.

AUTHORS:

- David Roe
"""
from __future__ import absolute_import

#*****************************************************************************
#       Copyright (C) 2007-2013 David Roe <roed.math@gmail.com>
#                               William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from .padic_generic import pAdicGeneric
from .padic_base_generic import pAdicBaseGeneric
from sage.structure.richcmp import op_EQ
from functools import reduce


class pAdicExtensionGeneric(pAdicGeneric):
    def __init__(self, poly, prec, print_mode, names, element_class):
        """
        Initialization

        EXAMPLES::

            sage: R = Zp(5,5)
            sage: S.<x> = R[]
            sage: f = x^5 + 75*x^3 - 15*x^2 +125*x - 5
            sage: W.<w> = R.ext(f) #indirect doctest
        """
        #type checking done in factory
        self._given_poly = poly
        R = poly.base_ring()
        # We'll deal with the different names better later.
        # Using a tuple here is mostly needed for more general extensions
        # (ie not eisenstein or unramified)
        print_mode['unram_name'] = names[2]
        print_mode['ram_name'] = names[3]
        print_mode['var_name'] = names[0]
        names = names[0]
        pAdicGeneric.__init__(self, R, R.prime(), prec, print_mode, names, element_class)
        self._populate_coercion_lists_(coerce_list=[R], element_constructor=element_class)

#     def __reduce__(self):
#         """
#         For pickling.

#         This function is provided because prime_pow needs to be set before _printer, so the standard unpickling fails.
#         """
#         from sage.rings.padics.factory import ExtensionFactory
#         return ExtensionFactory, (self.base_ring(), self._exact_modulus, self.precision_cap(), self.print_mode(), None, self.variable_name())

    def _coerce_map_from_(self, R):
        """
        Returns True if there is a coercion map from R to self.

        EXAMPLES::

            sage: R = Zp(5); S.<x> = ZZ[]; f = x^5 + 25*x - 5; W.<w> = R.ext(f)
            sage: L = W.fraction_field()
            sage: w + L(w) #indirect doctest
            2*w + O(w^101)
            sage: w + R(5,2)
            w + w^5 + O(w^10)
        """
        # Far more functionality needs to be added here later.
        if isinstance(R, pAdicExtensionGeneric) and R.fraction_field() is self:
            if self._implementation == 'NTL':
                return True
            elif R._prec_type() == 'capped-abs':
                from sage.rings.padics.qadic_flint_CA import pAdicCoercion_CA_frac_field as coerce_map
            elif R._prec_type() == 'capped-rel':
                from sage.rings.padics.qadic_flint_CR import pAdicCoercion_CR_frac_field as coerce_map
            elif R._prec_type() == 'floating-point':
                from sage.rings.padics.qadic_flint_FP import pAdicCoercion_FP_frac_field as coerce_map
            return coerce_map(R, self)

    def __eq__(self, other):
        """
        Return ``True`` if ``self == other`` and ``False`` otherwise.

        We consider two `p`-adic rings or fields to be equal if they are
        equal mathematically, and also have the same precision cap and
        printing parameters.

        EXAMPLES::

            sage: R.<a> = Qq(27)
            sage: S.<a> = Qq(27,print_mode='val-unit')
            sage: R == S
            False
            sage: S.<a> = Qq(27,type='capped-rel')
            sage: R == S
            True
            sage: R is S
            True
        """
        if not isinstance(other, pAdicExtensionGeneric):
            return False

        return (self.ground_ring() == other.ground_ring() and
                self.defining_polynomial() == other.defining_polynomial() and
                self.precision_cap() == other.precision_cap() and
                self._printer.richcmp_modes(other._printer, op_EQ))

    def __ne__(self, other):
        """
        Test inequality.

        EXAMPLES::

            sage: R.<a> = Qq(27)
            sage: S.<a> = Qq(27,print_mode='val-unit')
            sage: R != S
            True
        """
        return not self.__eq__(other)

    #def absolute_discriminant(self):
    #    raise NotImplementedError

    #def discriminant(self):
    #    raise NotImplementedError

    #def is_abelian(self):
    #    raise NotImplementedError

    #def is_normal(self):
    #    raise NotImplementedError

    def degree(self):
        """
        Returns the degree of this extension.

        EXAMPLES::

            sage: R.<a> = Zq(125); R.degree()
            3
            sage: R = Zp(5); S.<x> = ZZ[]; f = x^5 - 25*x^3 + 5; W.<w> = R.ext(f)
            sage: W.degree()
            5
        """
        return self._given_poly.degree()

    def defining_polynomial(self, exact=False):
        """
        Returns the polynomial defining this extension.

        INPUT:

        - ``exact`` -- boolean (default ``False``), whether to return the underlying exact
                       defining polynomial rather than the one with coefficients in the base ring.

        EXAMPLES::

            sage: R = Zp(5,5)
            sage: S.<x> = R[]
            sage: f = x^5 + 75*x^3 - 15*x^2 + 125*x - 5
            sage: W.<w> = R.ext(f)
            sage: W.defining_polynomial()
            (1 + O(5^5))*x^5 + (O(5^6))*x^4 + (3*5^2 + O(5^6))*x^3 + (2*5 + 4*5^2 + 4*5^3 + 4*5^4 + 4*5^5 + O(5^6))*x^2 + (5^3 + O(5^6))*x + (4*5 + 4*5^2 + 4*5^3 + 4*5^4 + 4*5^5 + O(5^6))
            sage: W.defining_polynomial(exact=True)
            x^5 + 75*x^3 - 15*x^2 + 125*x - 5

        .. SEEALSO::

            :meth:`modulus`
            :meth:`exact_field`
        """
        if exact:
            return self._exact_modulus
        else:
            return self._given_poly

    def exact_field(self):
        r"""
        Return a number field with the same defining polynomial.

        Note that this method always returns a field, even for a `p`-adic
        ring.

        EXAMPLES::

            sage: R = Zp(5,5)
            sage: S.<x> = R[]
            sage: f = x^5 + 75*x^3 - 15*x^2 +125*x - 5
            sage: W.<w> = R.ext(f)
            sage: W.exact_field()
            Number Field in w with defining polynomial x^5 + 75*x^3 - 15*x^2 + 125*x - 5

        .. SEEALSO::

            :meth:`defining_polynomial`
            :meth:`modulus`
        """
        return self.base_ring().exact_field().extension(self._exact_modulus, self.variable_name())

    def modulus(self, exact=False):
        r"""
        Returns the polynomial defining this extension.

        INPUT:

        - ``exact`` -- boolean (default ``False``), whether to return the underlying exact
                       defining polynomial rather than the one with coefficients in the base ring.

        EXAMPLES::

            sage: R = Zp(5,5)
            sage: S.<x> = R[]
            sage: f = x^5 + 75*x^3 - 15*x^2 +125*x - 5
            sage: W.<w> = R.ext(f)
            sage: W.modulus()
            (1 + O(5^5))*x^5 + (O(5^6))*x^4 + (3*5^2 + O(5^6))*x^3 + (2*5 + 4*5^2 + 4*5^3 + 4*5^4 + 4*5^5 + O(5^6))*x^2 + (5^3 + O(5^6))*x + (4*5 + 4*5^2 + 4*5^3 + 4*5^4 + 4*5^5 + O(5^6))
            sage: W.modulus(exact=True)
            x^5 + 75*x^3 - 15*x^2 + 125*x - 5

        .. SEEALSO::

            :meth:`defining_polynomial`
            :meth:`exact_field`
        """
        return self.defining_polynomial(exact)

    def ground_ring(self):
        """
        Returns the ring of which this ring is an extension.

        EXAMPLES::

            sage: R = Zp(5,5)
            sage: S.<x> = R[]
            sage: f = x^5 + 75*x^3 - 15*x^2 +125*x - 5
            sage: W.<w> = R.ext(f)
            sage: W.ground_ring()
            5-adic Ring with capped relative precision 5
        """
        return self._given_poly.base_ring()

    def ground_ring_of_tower(self):
        """
        Returns the p-adic base ring of which this is ultimately an
        extension.

        Currently this function is identical to ground_ring(), since
        relative extensions have not yet been implemented.

        EXAMPLES::

            sage: Qq(27,30,names='a').ground_ring_of_tower()
            3-adic Field with capped relative precision 30
        """
        if isinstance(self.ground_ring(), pAdicBaseGeneric):
            return self.ground_ring()
        else:
            return self.ground_ring().ground_ring_of_tower()

    #def is_isomorphic(self, ring):
    #    raise NotImplementedError

    def polynomial_ring(self):
        """
        Returns the polynomial ring of which this is a quotient.

        EXAMPLES::

            sage: Qq(27,30,names='a').polynomial_ring()
            Univariate Polynomial Ring in x over 3-adic Field with capped relative precision 30
        """
        return self._given_poly.parent()

    #def teichmuller(self, x, prec = None):
    #    if prec is None:
    #        prec = self.precision_cap()
    #    x = self(x, prec)
    #    if x.valuation() > 0:
    #        return self(0)
    #    q = self.residue_class_field().order()
    #    u = 1 / self(1 - q, prec)
    #    delta = u * (1 - x ** (q - 1))
    #    xnew = x - x*delta*(1 - q * delta)
    #    while x != xnew:
    #        x = xnew
    #        delta = u*(1-x**(q-1))
    #        xnew = x - x*delta*(1-q*delta)
    #    return x

    def construction(self):
        """
        Returns the functorial construction of this ring, namely,
        the algebraic extension of the base ring defined by the given
        polynomial.

        Also preserves other information that makes this ring unique
        (e.g. precision, rounding, print mode).

        EXAMPLES::

            sage: R.<a> = Zq(25, 8, print_mode='val-unit')
            sage: c, R0 = R.construction(); R0
            5-adic Ring with capped relative precision 8
            sage: c(R0)
            Unramified Extension in a defined by x^2 + 4*x + 2 with capped relative precision 8 over 5-adic Ring
            sage: c(R0) == R
            True
        """
        from sage.categories.pushout import AlgebraicExtensionFunctor as AEF
        print_mode = self._printer.dict()
        return (AEF([self.defining_polynomial(exact=True)], [self.variable_name()],
                    prec=self.precision_cap(), print_mode=self._printer.dict(),
                    implementation=self._implementation),
                self.base_ring())

    def fraction_field(self, print_mode=None):
        r"""
        Returns the fraction field of this extension, which is just
        the extension of base.fraction_field() determined by the
        same polynomial.

        INPUT:

        - print_mode -- a dictionary containing print options.
          Defaults to the same options as this ring.

        OUTPUT:

        - the fraction field of self.

        EXAMPLES::

            sage: U.<a> = Zq(17^4, 6, print_mode='val-unit', print_max_terse_terms=3)
            sage: U.fraction_field()
            Unramified Extension in a defined by x^4 + 7*x^2 + 10*x + 3 with capped relative precision 6 over 17-adic Field
            sage: U.fraction_field({"pos":False}) == U.fraction_field()
            False
        """
        if self.is_field() and print_mode is None:
            return self
        if print_mode is None:
            return self.change(field=True)
        else:
            return self.change(field=True, **print_mode)

    def integer_ring(self, print_mode=None):
        r"""
        Returns the ring of integers of self, which is just the
        extension of base.integer_ring() determined by the same
        polynomial.

        INPUT:

            - print_mode -- a dictionary containing print options.
              Defaults to the same options as this ring.

        OUTPUT:

            - the ring of elements of self with nonnegative valuation.

        EXAMPLES::

            sage: U.<a> = Qq(17^4, 6, print_mode='val-unit', print_max_terse_terms=3)
            sage: U.integer_ring()
            Unramified Extension in a defined by x^4 + 7*x^2 + 10*x + 3 with capped relative precision 6 over 17-adic Ring
            sage: U.fraction_field({"pos":False}) == U.fraction_field()
            False
        """
        #Currently does not support fields with non integral defining polynomials.  This should change when the padic_general_extension framework gets worked out.
        if not self.is_field() and print_mode is None:
            return self
        if print_mode is None:
            return self.change(field=False)
        else:
            return self.change(field=False, **print_mode)

    #def hasGNB(self):
    #    raise NotImplementedError

    def random_element(self):
        """
        Returns a random element of self.

        This is done by picking a random element of the ground ring
        self.degree() times, then treating those elements as
        coefficients of a polynomial in self.gen().

        EXAMPLES::

            sage: R.<a> = Zq(125, 5); R.random_element()
            (3*a^2 + 3*a + 3) + (a^2 + 4*a + 1)*5 + (3*a^2 + 4*a + 1)*5^2 + 
            (2*a^2 + 3*a + 3)*5^3 + (4*a^2 + 3)*5^4 + O(5^5)
            sage: R = Zp(5,3); S.<x> = ZZ[]; f = x^5 + 25*x^2 - 5; W.<w> = R.ext(f)
            sage: W.random_element()
            4 + 3*w + w^2 + 4*w^3 + w^5 + 3*w^6 + w^7 + 4*w^10 + 2*w^12 + 4*w^13 + 3*w^14 + O(w^15)
        """
        return reduce(lambda x,y: x+y,
                      [self.ground_ring().random_element() * self.gen()**i for i in
                           range(self.modulus().degree())],
                      0)

    #def unit_group(self):
    #    raise NotImplementedError

    #def unit_group_gens(self):
    #    raise NotImplementedError

    #def principal_unit_group(self):
    #    raise NotImplementedError

    #def zeta(self, n = None):
    #    raise NotImplementedError

    #def zeta_order(self):
    #    raise NotImplementedError

