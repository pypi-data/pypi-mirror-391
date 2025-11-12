/** ***** lsdelta_py.c *****
 *
 * Copyright (c) 2024 Hauke Daempfling (haukex@zero-g.net)
 * at the Leibniz Institute of Freshwater Ecology and Inland Fisheries (IGB),
 * Berlin, Germany, https://www.igb-berlin.de/
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program. If not, see https://www.gnu.org/licenses/
 */

// https://docs.python.org/3.10/extending/index.html
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdbool.h>

//#define LSDELTA_DEBUG

bool _get_dec_dig(const char *str, const Py_ssize_t len, Py_ssize_t *cnt) {
	bool found_dec = false;
	*cnt = 0;
	Py_ssize_t dig_cnt = 0;
	for ( Py_ssize_t i=0; i<len; i++ ) {
		if (strchr(i ? ".0123456789" : "+-.0123456789", str[i])==NULL) {
			PyErr_SetString(PyExc_ValueError, "illegal character in decimal number");
			return false;
		}
		if (str[i]=='.') {  // found *a* decimal point
			if (found_dec) {
				PyErr_SetString(PyExc_ValueError, "more than one decimal point");
				return false;
			}
			found_dec = true;
		}
		else {
			if ( str[i]!='-' && str[i]!='+' )  // count digits
				dig_cnt++;
			if (found_dec)  // count digits after decimal
				(*cnt)++;
		}
	}
	if (dig_cnt<1) {  // no digits seen at all! (empty string, "+", "-.", etc.)
		PyErr_SetString(PyExc_ValueError, "no digits in number");
		return false;
	}
#ifdef LSDELTA_DEBUG
	printf("Digits: <<%s>> => %ld\n", str, *cnt);
#endif
	return true;
}

PyObject *_convert(const char *str, const Py_ssize_t len, Py_ssize_t pad) {

	// initialize the output string
	// https://docs.python.org/3.10/c-api/memory.html#raw-memory-interface
	const Py_ssize_t new_len = len+pad;
	char *out = (char*) PyMem_RawMalloc(new_len+1);  // +1 NUL!
	if (out==NULL) {
		PyErr_SetString(PyExc_MemoryError, "malloc failed");
		return NULL;
	}

#ifdef LSDELTA_DEBUG
	printf("Convert: <<%s>> (new_len=%ld) ", str, new_len); fflush(stdout);
#endif
	// copy over without decimal point
	Py_ssize_t o = 0;
	for( Py_ssize_t i=0; i<len; i++ ) {
		assert(o<new_len);
		if (str[i]!='.')
			out[o++] = str[i];
	}
	// pad
	for ( Py_ssize_t i=0; i<pad; i++ ) {
		assert(o<new_len);
		out[o++] = '0';
	}
	assert(o<=new_len);  // ok because of new_len+1 above
	out[o] = '\0';
#ifdef LSDELTA_DEBUG
	printf("=> <<%s>>\n", out); fflush(stdout);
#endif

	// convert to number
	// https://docs.python.org/3.10/c-api/long.html#c.PyLong_FromString
	PyObject* num = PyLong_FromString(out, NULL, 10);
	PyMem_RawFree(out);  // free this immediately to make error handling easier
	if (num==NULL) return NULL;

	return num;
}

static PyObject *
lsdelta(PyObject *Py_UNUSED(self), PyObject *args) {
	const char *a;
	Py_ssize_t a_len;
	const char *b;
	Py_ssize_t b_len;

	// https://docs.python.org/3.10/c-api/arg.html#strings-and-buffers
    if (!PyArg_ParseTuple(args, "s#s#", &a, &a_len, &b, &b_len))
		return NULL;

	// check strings and get number of digits after decimal point
	Py_ssize_t a_cnt;
	if (!_get_dec_dig(a, a_len, &a_cnt))
		return NULL;
	Py_ssize_t b_cnt;
	if (!_get_dec_dig(b, b_len, &b_cnt))
		return NULL;

	// convert the strings to numbers
	PyObject *a_num = _convert(a, a_len, b_cnt>a_cnt ? b_cnt-a_cnt : 0);
	if (a_num==NULL) return NULL;
	PyObject *b_num = _convert(b, b_len, a_cnt>b_cnt ? a_cnt-b_cnt : 0);
	if (b_num==NULL) {
		Py_DECREF(a_num);
		return NULL;
	}

	// do the delta
	// https://docs.python.org/3.10/c-api/number.html#c.PyNumber_Subtract
	PyObject* rv = PyNumber_Subtract(a_num, b_num);
	Py_DECREF(a_num);
	Py_DECREF(b_num);
    return rv;
}

static PyMethodDef lsdelta_methods[] = {
    {"lsdelta",  lsdelta, METH_VARARGS,
	"This function takes two decimal numbers stored as strings, \
	pads them both to the same length after the decimal point, \
	and then removes the decimal point and subtracts them, \
	giving you the difference in their least significant digits."},
    {NULL, NULL, 0, NULL}  // Sentinel
};

static struct PyModuleDef_Slot module_slots[] = {
#if PY_VERSION_HEX >= 0x030D0000
    {Py_mod_gil, Py_MOD_GIL_USED},
#endif
    {0, NULL}  // Sentinel
};

static struct PyModuleDef lsdelta_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "lsdelta",
    .m_size = 0,
    .m_methods = lsdelta_methods,
	.m_slots = module_slots
};

PyMODINIT_FUNC
PyInit_lsdelta(void) {
    return PyModuleDef_Init(&lsdelta_module);
}
