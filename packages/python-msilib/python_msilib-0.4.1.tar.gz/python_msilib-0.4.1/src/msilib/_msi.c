/* Helper library for MSI creation with Python.
 * Copyright (C) 2005 Martin v. Löwis
 * Licensed to PSF under a contributor agreement.
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
// clang-format off
#include <windows.h>
// clang-format on
#include "include/pythoncapi_compat.h"
#include <fci.h>
#include <fcntl.h>
#include <msi.h>
#include <msidefs.h>
#include <msiquery.h>
#include <rpc.h>

/*[clinic input]
module _msi
class _msi.Record "msiobj *" "&record_Type"
class _msi.SummaryInformation "msiobj *" "&summary_Type"
class _msi.View "msiobj *" "&msiview_Type"
class _msi.Database "msiobj *" "&msidb_Type"
[clinic start generated code]*/
/*[clinic end generated code: output=da39a3ee5e6b4b0d input=89a3605762cf4bdc]*/

static PyObject* MSIError;

/*[clinic input]
_msi.UuidCreate

Return the string representation of a new unique identifier.
[clinic start generated code]*/

static PyObject* _msi_UuidCreate_impl(PyObject* module)
/*[clinic end generated code: output=534ecf36f10af98e input=168024ab4b3e832b]*/
{
    UUID result;
    wchar_t* cresult;
    PyObject* oresult;

    /* May return ok, local only, and no address.
       For local only, the documentation says we still get a uuid.
       For RPC_S_UUID_NO_ADDRESS, it's not clear whether we can
       use the result. */
    if (UuidCreate(&result) == RPC_S_UUID_NO_ADDRESS) {
        PyErr_SetString(
            PyExc_NotImplementedError, "processing 'no address' result");
        return NULL;
    }

    if (UuidToStringW(&result, &cresult) == RPC_S_OUT_OF_MEMORY) {
        PyErr_SetString(PyExc_MemoryError, "out of memory in uuidgen");
        return NULL;
    }

    oresult = PyUnicode_FromWideChar(cresult, wcslen(cresult));
    RpcStringFreeW(&cresult);
    return oresult;
}

/* Helper for converting file names from UTF-8 to wchat_t*.  */
static wchar_t* utf8_to_wchar(const char* s, int* err)
{
    PyObject* obj = PyUnicode_FromString(s);
    if (obj == NULL) {
        if (PyErr_ExceptionMatches(PyExc_MemoryError)) {
            *err = ENOMEM;
        } else {
            *err = EINVAL;
        }
        PyErr_Clear();
        return NULL;
    }
    wchar_t* ws = PyUnicode_AsWideCharString(obj, NULL);
    if (ws == NULL) {
        *err = ENOMEM;
        PyErr_Clear();
    }
    Py_DECREF(obj);
    return ws;
}

/* FCI callback functions */

static FNFCIALLOC(cb_alloc) { return PyMem_RawMalloc(cb); }

static FNFCIFREE(cb_free) { PyMem_RawFree(memory); }

static FNFCIOPEN(cb_open)
{
    wchar_t* ws = utf8_to_wchar(pszFile, err);
    if (ws == NULL) {
        return -1;
    }
    int result = _wopen(ws, oflag | O_NOINHERIT, pmode);
    PyMem_Free(ws);
    if (result == -1)
        *err = errno;
    return result;
}

static FNFCIREAD(cb_read)
{
    UINT result = (UINT)_read((int)hf, memory, cb);
    if (result != cb)
        *err = errno;
    return result;
}

static FNFCIWRITE(cb_write)
{
    UINT result = (UINT)_write((int)hf, memory, cb);
    if (result != cb)
        *err = errno;
    return result;
}

static FNFCICLOSE(cb_close)
{
    int result = _close((int)hf);
    if (result != 0)
        *err = errno;
    return result;
}

static FNFCISEEK(cb_seek)
{
    long result = (long)_lseek((int)hf, dist, seektype);
    if (result == -1)
        *err = errno;
    return result;
}

static FNFCIDELETE(cb_delete)
{
    wchar_t* ws = utf8_to_wchar(pszFile, err);
    if (ws == NULL) {
        return -1;
    }
    int result = _wremove(ws);
    PyMem_Free(ws);
    if (result != 0)
        *err = errno;
    return result;
}

static FNFCIFILEPLACED(cb_fileplaced) { return 0; }

static FNFCIGETTEMPFILE(cb_gettempfile)
{
    char* name = _tempnam("", "tmp");
    if ((name != NULL) && ((int)strlen(name) < cbTempName)) {
        strcpy(pszTempName, name);
        free(name);
        return TRUE;
    }

    if (name)
        free(name);
    return FALSE;
}

static FNFCISTATUS(cb_status)
{
    if (pv) {
        PyObject* result
            = PyObject_CallMethod(pv, "status", "iii", typeStatus, cb1, cb2);
        if (result == NULL)
            return -1;
        Py_DECREF(result);
    }
    return 0;
}

static FNFCIGETNEXTCABINET(cb_getnextcabinet)
{
    if (pv) {
        PyObject* result
            = PyObject_CallMethod(pv, "getnextcabinet", "i", pccab->iCab);
        if (result == NULL)
            return -1;
        if (!PyBytes_Check(result)) {
            PyErr_Format(PyExc_TypeError,
                "Incorrect return type %s from getnextcabinet",
                Py_TYPE(result)->tp_name);
            Py_DECREF(result);
            return FALSE;
        }
        strncpy(pccab->szCab, PyBytes_AsString(result), sizeof(pccab->szCab));
        return TRUE;
    }
    return FALSE;
}

static FNFCIGETOPENINFO(cb_getopeninfo)
{
    BY_HANDLE_FILE_INFORMATION bhfi;
    FILETIME filetime;
    HANDLE handle;

    wchar_t* ws = utf8_to_wchar(pszName, err);
    if (ws == NULL) {
        return -1;
    }

    /* Need Win32 handle to get time stamps */
    handle = CreateFileW(ws, GENERIC_READ, FILE_SHARE_READ, NULL,
        OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (handle == INVALID_HANDLE_VALUE) {
        PyMem_Free(ws);
        return -1;
    }

    if (GetFileInformationByHandle(handle, &bhfi) == FALSE) {
        CloseHandle(handle);
        PyMem_Free(ws);
        return -1;
    }

    FileTimeToLocalFileTime(&bhfi.ftLastWriteTime, &filetime);
    FileTimeToDosDateTime(&filetime, pdate, ptime);

    *pattribs = (int)(bhfi.dwFileAttributes
        & (_A_RDONLY | _A_SYSTEM | _A_HIDDEN | _A_ARCH));

    CloseHandle(handle);

    int result = _wopen(ws, _O_RDONLY | _O_BINARY | O_NOINHERIT);
    PyMem_Free(ws);
    return result;
}

/*[clinic input]
_msi.FCICreate
    cabname: str
        the name of the CAB file
    files: object
        a list of tuples, each containing the name of the file on disk,
        and the name of the file inside the CAB file
    /

Create a new CAB file.
[clinic start generated code]*/

static PyObject* _msi_FCICreate_impl(
    PyObject* module, const char* cabname, PyObject* files)
/*[clinic end generated code: output=55dc05728361b799 input=1d2d75fdc8b44b71]*/
{
    const char* p;
    CCAB ccab;
    HFCI hfci;
    ERF erf;
    Py_ssize_t i;

    if (!PyList_Check(files)) {
        PyErr_SetString(PyExc_TypeError, "FCICreate expects a list");
        return NULL;
    }

    ccab.cb = INT_MAX; /* no need to split CAB into multiple media */
    ccab.cbFolderThresh = 1000000; /* flush directory after this many bytes */
    ccab.cbReserveCFData = 0;
    ccab.cbReserveCFFolder = 0;
    ccab.cbReserveCFHeader = 0;

    ccab.iCab = 1;
    ccab.iDisk = 1;

    ccab.setID = 0;
    ccab.szDisk[0] = '\0';

    for (i = 0, p = cabname; *p; p++)
        if (*p == '\\' || *p == '/')
            i = p - cabname + 1;

    if (i >= sizeof(ccab.szCabPath)
        || strlen(cabname + i) >= sizeof(ccab.szCab)) {
        PyErr_SetString(PyExc_ValueError, "path name too long");
        return 0;
    }

    if (i > 0) {
        memcpy(ccab.szCabPath, cabname, i);
        ccab.szCabPath[i] = '\0';
        strcpy(ccab.szCab, cabname + i);
    } else {
        strcpy(ccab.szCabPath, ".\\");
        strcpy(ccab.szCab, cabname);
    }

    hfci = FCICreate(&erf, cb_fileplaced, cb_alloc, cb_free, cb_open, cb_read,
        cb_write, cb_close, cb_seek, cb_delete, cb_gettempfile, &ccab, NULL);

    if (hfci == NULL) {
        PyErr_Format(PyExc_ValueError, "FCI error %d", erf.erfOper);
        return NULL;
    }

    for (i = 0; i < PyList_Size(files); i++) {
        PyObject* item = PyList_GetItemRef(files, i);
        char *filename, *cabname;

        if (!PyArg_ParseTuple(item, "ss", &filename, &cabname)) {
            PyErr_SetString(PyExc_TypeError,
                "FCICreate expects a list of tuples containing two strings");
            FCIDestroy(hfci);
            return NULL;
        }

        if (!FCIAddFile(hfci, filename, cabname, FALSE, cb_getnextcabinet,
                cb_status, cb_getopeninfo, tcompTYPE_MSZIP))
            goto err;
    }

    if (!FCIFlushCabinet(hfci, FALSE, cb_getnextcabinet, cb_status))
        goto err;

    if (!FCIDestroy(hfci))
        goto err;

    Py_RETURN_NONE;
err:
    if (erf.fError)
        PyErr_Format(PyExc_ValueError, "FCI error %d",
            erf.erfOper); /* XXX better error type */
    else
        PyErr_SetString(PyExc_ValueError, "FCI general error");

    FCIDestroy(hfci);
    return NULL;
}

typedef struct msiobj {
    PyObject_HEAD MSIHANDLE h;
} msiobj;

static void msiobj_dealloc(msiobj* msidb)
{
    MsiCloseHandle(msidb->h);
    msidb->h = 0;
    PyObject_Free(msidb);
}

static PyObject* msierror(int status)
{
    int code;
    char buf[2000];
    char* res = buf;
    DWORD size = Py_ARRAY_LENGTH(buf);
    MSIHANDLE err = MsiGetLastErrorRecord();

    if (err == 0) {
        switch (status) {
        case ERROR_ACCESS_DENIED:
            PyErr_SetString(MSIError, "access denied");
            return NULL;
        case ERROR_FUNCTION_FAILED:
            PyErr_SetString(MSIError, "function failed");
            return NULL;
        case ERROR_INVALID_DATA:
            PyErr_SetString(MSIError, "invalid data");
            return NULL;
        case ERROR_INVALID_HANDLE:
            PyErr_SetString(MSIError, "invalid handle");
            return NULL;
        case ERROR_INVALID_STATE:
            PyErr_SetString(MSIError, "invalid state");
            return NULL;
        case ERROR_INVALID_PARAMETER:
            PyErr_SetString(MSIError, "invalid parameter");
            return NULL;
        case ERROR_OPEN_FAILED:
            PyErr_SetString(MSIError, "open failed");
            return NULL;
        case ERROR_CREATE_FAILED:
            PyErr_SetString(MSIError, "create failed");
            return NULL;
        default:
            PyErr_Format(MSIError, "unknown error %x", status);
            return NULL;
        }
    }

    code = MsiRecordGetInteger(err, 1); /* XXX code */
    if (MsiFormatRecord(0, err, res, &size) == ERROR_MORE_DATA) {
        res = malloc(size + 1);
        if (res == NULL) {
            MsiCloseHandle(err);
            return PyErr_NoMemory();
        }
        MsiFormatRecord(0, err, res, &size);
        res[size] = '\0';
    }
    MsiCloseHandle(err);
    PyErr_SetString(MSIError, res);
    if (res != buf)
        free(res);
    return NULL;
}

#include "include/_msi.h"

/*[clinic input]
_msi.Database.Close

Close the database object.
[clinic start generated code]*/

static PyObject* _msi_Database_Close_impl(msiobj* self)
/*[clinic end generated code: output=ddf2d7712ea804f1 input=104330ce4a486187]*/
{
    int status;
    if ((status = MsiCloseHandle(self->h)) != ERROR_SUCCESS) {
        return msierror(status);
    }
    self->h = 0;
    Py_RETURN_NONE;
}

/*************************** Record objects **********************/

/*[clinic input]
_msi.Record.GetFieldCount

Return the number of fields of the record.
[clinic start generated code]*/

static PyObject* _msi_Record_GetFieldCount_impl(msiobj* self)
/*[clinic end generated code: output=112795079c904398 input=5fb9d4071b28897b]*/
{
    return PyLong_FromLong(MsiRecordGetFieldCount(self->h));
}

/*[clinic input]
_msi.Record.GetInteger
    field: unsigned_int(bitwise=True)
    /

Return the value of field as an integer where possible.
[clinic start generated code]*/

static PyObject* _msi_Record_GetInteger_impl(msiobj* self, unsigned int field)
/*[clinic end generated code: output=7174ebb6e8ed1c79 input=d19209947e2bfe61]*/
{
    int status;

    status = MsiRecordGetInteger(self->h, field);
    if (status == MSI_NULL_INTEGER) {
        PyErr_SetString(MSIError, "could not convert record field to integer");
        return NULL;
    }
    return PyLong_FromLong((long)status);
}

/*[clinic input]
_msi.Record.GetString
    field: unsigned_int(bitwise=True)
    /

Return the value of field as a string where possible.
[clinic start generated code]*/

static PyObject* _msi_Record_GetString_impl(msiobj* self, unsigned int field)
/*[clinic end generated code: output=f670d1b484cfa47c input=ffa11f21450b77d8]*/
{
    unsigned int status;
    WCHAR buf[2000];
    WCHAR* res = buf;
    DWORD size = Py_ARRAY_LENGTH(buf);
    PyObject* string;

    status = MsiRecordGetStringW(self->h, field, res, &size);
    if (status == ERROR_MORE_DATA) {
        res = (WCHAR*)malloc((size + 1) * sizeof(WCHAR));
        if (res == NULL)
            return PyErr_NoMemory();
        status = MsiRecordGetStringW(self->h, field, res, &size);
    }
    if (status != ERROR_SUCCESS)
        return msierror((int)status);
    string = PyUnicode_FromWideChar(res, size);
    if (buf != res)
        free(res);
    return string;
}

/*[clinic input]
_msi.Record.ClearData

Set all fields of the record to 0.
[clinic start generated code]*/

static PyObject* _msi_Record_ClearData_impl(msiobj* self)
/*[clinic end generated code: output=1891467214b977f4 input=2a911c95aaded102]*/
{
    int status = MsiRecordClearData(self->h);
    if (status != ERROR_SUCCESS)
        return msierror(status);

    Py_RETURN_NONE;
}

/*[clinic input]
_msi.Record.SetString
    field: int
    value: wchar_t
    /

Set field to a string value.
[clinic start generated code]*/

static PyObject* _msi_Record_SetString_impl(
    msiobj* self, int field, const wchar_t* value)
/*[clinic end generated code: output=2e37505b0f11f985 input=fb8ec70a2a6148e0]*/
{
    int status;

    if ((status = MsiRecordSetStringW(self->h, field, value)) != ERROR_SUCCESS)
        return msierror(status);

    Py_RETURN_NONE;
}

/*[clinic input]
_msi.Record.SetStream
    field: int
    value: wchar_t
    /

Set field to the contents of the file named value.
[clinic start generated code]*/

static PyObject* _msi_Record_SetStream_impl(
    msiobj* self, int field, const wchar_t* value)
/*[clinic end generated code: output=442facac16913b48 input=a07aa19b865e8292]*/
{
    int status;

    if ((status = MsiRecordSetStreamW(self->h, field, value)) != ERROR_SUCCESS)
        return msierror(status);

    Py_RETURN_NONE;
}

/*[clinic input]
_msi.Record.SetInteger
    field: int
    value: int
    /

Set field to an integer value.
[clinic start generated code]*/

static PyObject* _msi_Record_SetInteger_impl(
    msiobj* self, int field, int value)
/*[clinic end generated code: output=669e8647775d0ce7 input=c571aa775e7e451b]*/
{
    int status;

    if ((status = MsiRecordSetInteger(self->h, field, value)) != ERROR_SUCCESS)
        return msierror(status);

    Py_RETURN_NONE;
}

static PyMethodDef record_methods[]
    = { _MSI_RECORD_GETFIELDCOUNT_METHODDEF, _MSI_RECORD_GETINTEGER_METHODDEF,
          _MSI_RECORD_GETSTRING_METHODDEF, _MSI_RECORD_SETSTRING_METHODDEF,
          _MSI_RECORD_SETSTREAM_METHODDEF, _MSI_RECORD_SETINTEGER_METHODDEF,
          _MSI_RECORD_CLEARDATA_METHODDEF, _MSI_SENTINEL };

static PyTypeObject record_Type = {
    PyVarObject_HEAD_INIT(NULL, 0) "_msi.Record", /*tp_name*/
    sizeof(msiobj),                               /*tp_basicsize*/
    0,                                            /*tp_itemsize*/
    /* methods */
    (destructor)msiobj_dealloc, /*tp_dealloc*/
    0,                          /*tp_vectorcall_offset*/
    0,                          /*tp_getattr*/
    0,                          /*tp_setattr*/
    0,                          /*tp_as_async*/
    0,                          /*tp_repr*/
    0,                          /*tp_as_number*/
    0,                          /*tp_as_sequence*/
    0,                          /*tp_as_mapping*/
    0,                          /*tp_hash*/
    0,                          /*tp_call*/
    0,                          /*tp_str*/
    PyObject_GenericGetAttr,    /*tp_getattro*/
    PyObject_GenericSetAttr,    /*tp_setattro*/
    0,                          /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,         /*tp_flags*/
    0,                          /*tp_doc*/
    0,                          /*tp_traverse*/
    0,                          /*tp_clear*/
    0,                          /*tp_richcompare*/
    0,                          /*tp_weaklistoffset*/
    0,                          /*tp_iter*/
    0,                          /*tp_iternext*/
    record_methods,             /*tp_methods*/
    0,                          /*tp_members*/
    0,                          /*tp_getset*/
    0,                          /*tp_base*/
    0,                          /*tp_dict*/
    0,                          /*tp_descr_get*/
    0,                          /*tp_descr_set*/
    0,                          /*tp_dictoffset*/
    0,                          /*tp_init*/
    0,                          /*tp_alloc*/
    0,                          /*tp_new*/
    0,                          /*tp_free*/
    0,                          /*tp_is_gc*/
};

static PyObject* record_new(MSIHANDLE h)
{
    msiobj* result = PyObject_New(struct msiobj, &record_Type);

    if (!result) {
        MsiCloseHandle(h);
        return NULL;
    }

    result->h = h;
    return (PyObject*)result;
}

/*************************** SummaryInformation objects **************/

/*[clinic input]
_msi.SummaryInformation.GetProperty
    field: int
        the name of the property, one of the PID_* constants
    /

Return a property of the summary.
[clinic start generated code]*/

static PyObject* _msi_SummaryInformation_GetProperty_impl(
    msiobj* self, int field)
/*[clinic end generated code: output=f8946a33ee14f6ef input=f8dfe2c890d6cb8b]*/
{
    int status;
    PyObject* result;
    UINT type;
    INT ival;
    FILETIME fval;
    char sbuf[1000];
    char* sval = sbuf;
    DWORD ssize = sizeof(sbuf);

    status = MsiSummaryInfoGetProperty(
        self->h, field, &type, &ival, &fval, sval, &ssize);
    if (status == ERROR_MORE_DATA) {
        ssize++;
        sval = malloc(ssize);
        if (sval == NULL) {
            return PyErr_NoMemory();
        }
        status = MsiSummaryInfoGetProperty(
            self->h, field, &type, &ival, &fval, sval, &ssize);
    }
    if (status != ERROR_SUCCESS) {
        return msierror(status);
    }

    switch (type) {
    case VT_I2:
    case VT_I4:
        result = PyLong_FromLong(ival);
        break;
    case VT_FILETIME:
        PyErr_SetString(PyExc_NotImplementedError, "FILETIME result");
        result = NULL;
        break;
    case VT_LPSTR:
        result = PyBytes_FromStringAndSize(sval, ssize);
        break;
    case VT_EMPTY:
        result = Py_NewRef(Py_None);
        break;
    default:
        PyErr_Format(PyExc_NotImplementedError, "result of type %d", type);
        result = NULL;
        break;
    }
    if (sval != sbuf)
        free(sval);
    return result;
}

/*[clinic input]
_msi.SummaryInformation.GetPropertyCount

Return the number of summary properties.
[clinic start generated code]*/

static PyObject* _msi_SummaryInformation_GetPropertyCount_impl(msiobj* self)
/*[clinic end generated code: output=68e94b2aeee92b3d input=2e71e985586d82dc]*/
{
    int status;
    UINT result;

    status = MsiSummaryInfoGetPropertyCount(self->h, &result);
    if (status != ERROR_SUCCESS)
        return msierror(status);

    return PyLong_FromLong(result);
}

/*[clinic input]
_msi.SummaryInformation.SetProperty
    field: int
        the name of the property, one of the PID_* constants
    value as data: object
        the new value of the property (integer or string)
    /

Set a property.
[clinic start generated code]*/

static PyObject* _msi_SummaryInformation_SetProperty_impl(
    msiobj* self, int field, PyObject* data)
/*[clinic end generated code: output=3d4692c8984bb675 input=f2a7811b905abbed]*/
{
    int status;

    if (PyUnicode_Check(data)) {
        WCHAR* value = PyUnicode_AsWideCharString(data, NULL);
        if (value == NULL) {
            return NULL;
        }
        status = MsiSummaryInfoSetPropertyW(
            self->h, field, VT_LPSTR, 0, NULL, value);
        PyMem_Free(value);
    } else if (PyLong_CheckExact(data)) {
        long value = PyLong_AsLong(data);
        if (value == -1 && PyErr_Occurred()) {
            return NULL;
        }
        status = MsiSummaryInfoSetProperty(
            self->h, field, VT_I4, value, NULL, NULL);
    } else {
        PyErr_SetString(PyExc_TypeError, "unsupported type");
        return NULL;
    }

    if (status != ERROR_SUCCESS)
        return msierror(status);

    Py_RETURN_NONE;
}

/*[clinic input]
_msi.SummaryInformation.PersisryInflalue == NULL) {
            return NULL;
        }
       ,ti***********sld, vnerated code]*/

static PyObject* _msi_SummaryInformation_SetProperty_impl(
 NULL) 
/*[clinic end generated code: output=68e94b2aeee92b3d inc564bd17f5e122cbfe61]*/e3dda9d530095ef7tus;

    status = MsiRecordGetInteger(seSetProperty NULL) (status != ERROR_SUCCESS)
        return msierror(status);

    Py_RETURN_NON
}

static PyMethodDef record_methods[]
 s _msi.V_MSI_RECORD_GETFIELDCOUNSUMMARY    FILETIMF, _PROPERTY    _MSI_RECORD_CLEARDATA_MESUMMARY    FILETIMF, _PROPERTYSI_RECORD_GETINTCORD_CLEARDATA_MESUMMARY    FILETIMFS _PROPERTY    _MSI_RECORD_CLEARDATA_MESUMMARY    FILETIMFPERSISTNTINEL };

static PyTypeObject record_Type = {
  s _msi.View ct_HEAD_INIT(NULL, 0) "_msi.Record", /*tp_name*SetProperty_impl( sizeof(msiobj),                               /*tp_basicsize*/
 sicsize*/
    0,                                            /*tp_itemsize*/
  emsize*/
    /* methods */
    (destructor)msiobj_dealloc, /*tp_dealloc*/
    0,                          /*tp_vectorcall_offset*/
    0,                          /*tp_getattr*/
    0,                          /*tp_setattr*/
    0,                          /*tp_as_async*/
    0,                          /*tp_repr*/
    0,                          /*tp_as_number*/
    0,                          /*tp_as_sequence*/
    0,                          /*tp_as_mapping*/
    0,                          /*tp_hash*/
    0,                          /*tp_call*/
    0,                          /*tp_str*/
    PyObject_GenericGetAttr,    /*tp_getattro*/
    PyObject_GenericSetAttr,    /*tp_setattro*/
    0,                          /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,         /*tp_flags*/
    0,                          /*tp_doc*/
    0,                          /*tp_traverse*/
    0,                          /*tp_clear*/
    0,                          /*tp_richcompare*/
    0,                          /*tp_weaklistoffset*/
    0,                          /*tp_iter*/
    0,                          /*tp_iternext*/
    record_methods,    s _msi.V_MSI_RE,thods*/
    0,                          /*tp_members*/
    0,                          /*tp_getset*/
    0,                          /*tp_base*/
    0,                          /*tp_dict*/
    0,                          /*tp_descr_get*/
    0,                          /*tp_descr_set*/
    0,                          /*tp_dictoffset*/
    0,                          /*tp_init*/
    0,                          /*tp_alloc*/
    0,                          /*tp_new*/
    0,                          /*tp_free*/
    0,                          /*tp_is_gc*/
};

static PyObject* re********* SummaryInformation sivie***/

/*[clinic input]
_msi.SummaryInformation.sivi.Execur
          s    o     s list of tuples, eacic star     ib sta   clud
    value.
       re   kenendswith(".pmary p<rpc.

S          t]
_Execurary pSQLp<rpc.
lue.
msi.nerated code]*/

static PyObject* _msi_SummaryInformation_sivi_Execurgned int field)nicode_From     snerated code: output=f8946a33ee14f6ef inp0f65fd2900bcb4e832b]*/cb163a15d453348etus;
    UINT result;

     msiobj*      s ab = 1;
   le(item_Is    (m     snErr_ExceptionMatctem_ISame);m     s
    if (!resulErr_SetString(PyExc_TypeError,
 y_TYPE(result)->tp_nupported type");Execura, orderi must excacic sta"urn NULL;
        }
    }

    code = Msi         s = (gned int)m     snus tch (type) {
   tInteger(sesiviExecurgI4, value     sn= ERROR_SUCCESS)
        return msierror(status);

    Py_RETURN_NONE;
}

/*[clinic input]
_msi.Record.SetString
 sivi.Fetchty of the sum     bric starlue.
<rpc.herated code]*/

static PyObject* _msi_SummaryInformation_sivi_Fetch
/*[clinic end generated code: output=68e94b2aeee92b3d inba154a3794537d4e832b]*/7f3e3d06c449001ctus;
    UINT result;

     msiobj* us = MsiSummaryInfoGetPropesiviFetch
    if (status != ERROR_SUCCESS)
 {
     NO    ssITEM_SetString(
   
/*[clinic inpung_CheckExact(dCESS) {
        return msierror(status);
    }

    switch (type) {
  
/*[clinh)
{
  linic input]
_msi.SummaryInformation.sivi.tatColumnerty {
  kin name of the pro  mCOL    _NAMES h PythCOL    _me);S property of the sumic star     ib sta file lumns
lue.
msi.nerated code]*/

static PyObject* _msi_SummaryInformation_sivi_tatColumnerty unsigned int field)NT rkin nerated code: output=68e94b2aeee92b3d ine7aa197db94036608292]*/fedb892bf564a3btus;
    UINT result;

     msiobj* us = MsiSummarycordSetInteger(sesivitatColumnerty
    if (kin  (status !sierror(sta        return msierror(status);

    return PyLong_FromLong(resinh)
{
  linic input]
_msi.SummaryInformation.sivi.Mretuy {
  kin name of the pronstants
    mMODIFYalue as data: obje   the new value of thumic star     ib sta filoperdds ofroperty oMretuyue.
msi.nerated code]*/

static PyObject* _msi_SummaryInformation_sivi_Mretuy unsigned int field)NT rkin /*[clinic end generated code: output=3d4692c8984bb675 in69aaf3ce8ddac0ba82dc]*/828de22de0d47b4tus;

    if (PyUnicode_Check(dattem_ISame);   if    if (!resulErr_SetStringxc_TypeError, "unsupported type");Mretuyuuples contr************ NULL;
    }

    if (status != ERROR_SUCSetInteger(sesiviMretuy
    if (kin  ((gned int)d gennic iierror(sta        return msierror(status);

    return PyLong_FromL

/*[clinic input]
_msi.Record.SetString
 sivi.database object.
[msi.nerated code]*/

static PyObject* _msi_SummaryInformation_sivi_self)
/*[clinic end generated code: output=ddf2d7712ea804f1 in488f7b8645ca104a82dc]*/de6927d1308c401ctus;
    UINT result;
 ERROR_SUCSetInteger(sesiviself)_SUCCESS) {
        return ierror(status);

    Py_RETURN_NONE;
}

static PyMethodDef record_methods[]
 msi.D_MSI_RECOTFIELDCOUNVIEW_EXEC
      _MSI_RECORD_CDCOUNVIEW_GETCOLUMo)
{NTINEL };

statVIEW_FETCH    _MSI_RECORD_CDCOUNVIEW_MODIFYaTINEL };

statVIEW_
    NTINEL };

static PyTypeObject record_Type = {
  s _msi.Databct_HEAD_INIT(NULL, 0) "_msi.Record", /*tp_name*sivi sizeof(msiobj),                               /*tp_basicsize*/   0,                                            /*tp_itemsize*/
  /* methods */
    (destructor)msiobj_dealloc, /*tp_dealloc*/
    0,                          /*tp_vectorcall_offset*/
    0,                          /*tp_getattr*/
    0,                          /*tp_setattr*/
    0,                          /*tp_as_async*/
    0,                          /*tp_repr*/
    0,                          /*tp_as_number*/
    0,                          /*tp_as_sequence*/
    0,                          /*tp_as_mapping*/
    0,                          /*tp_hash*/
    0,                          /*tp_call*/
    0,                          /*tp_str*/
    PyObject_GenericGetAttr,    /*tp_getattro*/
    PyObject_GenericSetAttr,    /*tp_setattro*/
    0,                          /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,         /*tp_flags*/
    0,                          /*tp_doc*/
    0,                          /*tp_traverse*/
    0,                          /*tp_clear*/
    0,                          /*tp_richcompare*/
    0,                          /*tp_weaklistoffset*/
    0,                          /*tp_iter*/
    0,                          /*tp_iternext*/
    record_methods,    msi.D_MSI_RE,_members*/
    0,                          /*tp_members*/
    0,                          /*tp_getset*/
    0,                          /*tp_base*/
    0,                          /*tp_dict*/
    0,                          /*tp_descr_get*/
    0,                          /*tp_descr_set*/
    0,                          /*tp_dictoffset*/
    0,                          /*tp_init*/
    0,                          /*tp_alloc*/
    0,                          /*tp_new*/
    0,                          /*tp_free*/
    0,                          /*tp_is_gc*/
};

static PyObject* re********* SummaryInformation Dlinic start ge
/*[clinic input]
_msi.SummaryInformation.lose the Opensivi),     ql
Set field to tf the prSQLp   rederi ETURxecur
     rty of the sumvivie***/
nerated code]*/

static PyObject* _msi_Database_Close_impl(msiobj* Opensivi unsigned int field)e)
/*[clinic e qlnerated code: output=68e94b2aeee92b3d ine712e6a11229abfd82dc]*/50f1771f37e500dftus;
    UINT result;

     msiobj* hsivi;t = PyObject_New(str
 ERROR_SUCSetInteger(se(msiobj*Opensivialue)) != E qlf  hsivi) {
        return ierror(status);

    Py_RETURN_NONE;
}ew(struct msiobj, &record_Type);

  s _msi.Datab!= ERROR_SUC MsiCloseHandle(h);
        return sivi)ULL;
    }

    result->h = h;
    return (PyObsivi;t = Pyesult;
}

/********************i.Database.Close

Close the dommi {
 dommi a filehanges pend stapmary p     ri Eransa     nerated code]*/

static PyObject* _msi_Database_Close_impl(msiobj* sommi 
/*[clinic end generated code: output=ddf2d7712ea804f1 inf33021feb8b0cdde8292]*/375bb120d402266dtus;
    UINT result;
 ERROR_SUCSetInteger(se(msiobj*sommi _SUCCESS) {
        return ierror(status);

    Py_RETURN_NONE;
}

static PyMethodDef **i.Database.Close

Close the  fieetProperty_impl(ordGetInuntname of the propertmaximumproperties.u   *ptart gea property of the sumoper      ,ti**************/
nerated code]*/

static PyObject* _msi_Database_Close_impl(msiobj*  fieetProperty_impl( self, int field, PyObject* daInuntnerated code: output=7174ebb6e8ed1c79 inp81e51a4ea4da84e451b]*/18a899ead6521735tus;
    UINT result;

     msiobj* us = MsiSnt field, Pyous = MsiSummaryInfoGetPrope fieetProperty_impl(lue)) != Erd", /Inunt (status != ERROR_SUCCESS)
        return msierror(status);

    return PyLong_FromLoew(struct msiobj, &record_Type);

  s _msi.View != ERROR_SUC oMsiCloseHandle(h);
        return   return FALSE;


    oresult = PyUnicode_FromWin (PyOus = MsiSnt fesult;
}

/****oc FNFCIFILEPLACED(cb_methods[]
 dbV_MSI_RECORD_GETFIELDCOUNize+BA  N    VIEW_MINEL };

statize+BA  NCOMMIECORD_GETINTCORD_CLEARDATA_MEize+BA  N, _MUMMARY    FILETIMFORD_GETINTCORD_CLEARDATA_MEize+BA  N
    NTINEL };

static PyTypeObject record_Type = {
  s _tart gect_HEAD_INIT(NULL, 0) "_msi.Record", /*tp_name*(msiobj* sizeof(msiobj),                               /*tp_basicsize*/
 si   0,                                            /*tp_itemsize*/
  em  /* methods */
    (destructor)msiobj_dealloc, /*tp_dealloc*/
    0,                          /*tp_vectorcall_offset*/
    0,                          /*tp_getattr*/
    0,                          /*tp_setattr*/
    0,                          /*tp_as_async*/
    0,                          /*tp_repr*/
    0,                          /*tp_as_number*/
    0,                          /*tp_as_sequence*/
    0,                          /*tp_as_mapping*/
    0,                          /*tp_hash*/
    0,                          /*tp_call*/
    0,                          /*tp_str*/
    PyObject_GenericGetAttr,    /*tp_getattro*/
    PyObject_GenericSetAttr,    /*tp_setattro*/
    0,                          /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,         /*tp_flags*/
    0,                          /*tp_doc*/
    0,                          /*tp_traverse*/
    0,                          /*tp_clear*/
    0,                          /*tp_richcompare*/
    0,                          /*tp_weaklistoffset*/
    0,                          /*tp_iter*/
    0,                          /*tp_iternext*/
    record_methods,    dbV_MSI_RE,tp_members*/
    0,                          /*tp_members*/
    0,                          /*tp_getset*/
    0,                          /*tp_base*/
    0,                          /*tp_dict*/
    0,                          /*tp_descr_get*/
    0,                          /*tp_descr_set*/
    0,                          /*tp_dictoffset*/
    0,                          /*tp_init*/
    0,                          /*tp_alloc*/
    0,                          /*tp_new*/
    0,                          /*tp_free*/
    0,                          /*tp_is_gc*/
};

static PyObject* re#define;
  OTFPERSIST(x,     )                /*tp_itemsize*/
  emsize*/
  \siobj_dx
   (SIZE_T)(    ) && x
   ((SIZE_T)(    ) |   mDB     PATCH
    iiere#define;
 
        ERSIST(x)                /*tp_itemsize*/
  emsize*/
    \siobj_d
  OTFPERSIST(x,   mDB       OPO_NO)   /*tp_itemsize*/
  emsize*/
    \siobj_____) {
  OTFPERSIST(x,   mDB     TRANSACT)p_itemsize*/
  emsize*/
    \siobj_____) {
  OTFPERSIST(x,   mDB     DIRECT)p_itemsize*/
  emsize*/
      \siobj_____) {
  OTFPERSIST(x,   mDB           )p_itemsize*/
  emsize*/
      \siobj_____) {
  OTFPERSIST(x,   mDB           DIRECT))Def **i.Database.Close

COpen(msiobj*
       th
Set field to tf the pr[clinic sants
    mate a new CpNULL) name of the propertpNULL)       ree property of the sumoperclinic start generated code]*/

static PyObject* _msi_Database_Close_implOpen(msiobj*t* module, const char* cabname, PyOb[clinic ep   stNT rpNULL) nerated code: output=ddf2d7712ea804f1 inp34b7202b745de0abbed]*/1300f3b97659559btus;
    UINT result;

     msiobj* h;t = PyObject_New(str
 ERROR(deWeinto mult
    ararya rpNULL)  icont
       mDB     *art generthe proOperr
Re,
  Open(msiobj* may ld, t as a strinossibpo
   */   d statoerthe prounuples o mbehavior.matRecord(0, 
 
        ERSIST(pNULL) nsierror(status);

    retETER:
            PyErUnicode_FrfoGetPropeOpen(msiobj*W(p   st(LPCWSTR)(SIZE_T)pNULL) f  h!= ERROR_SUCCESS)
        return msierror(status);

    return PyLong_FromLon(struct msiobj, &record_Type);

  s _tart ge!= ERROR_SUC MsiCloseHandle(h);
        return NULL;
    }
    return PyLong_FromLoneturn (PyObject*)result;
}

/********************i.Database.Close

Cst of /
   ordGetInuntname of the propert the record.
[clinic start ge property of the sumoperr************nerated code]*/

static PyObject* _msi_Database_Close_implst of /
   t* modonst char* cabname* daInuntnerated code: output=7174ebb6e8ed1c79 in0ba0a00beea3e99e832b]*/53f17d5b5d9b077dtus;
    UI  msiobj* h;t ate(&erelf->h)t of /
   (Inuntn= INVALID_HAwitch ierror(status);

    ret0Long_FromLong(resinh)
{
  h)IFILEPLACED(cb_methods[]
 impl_MSI_RECOTFIELDCOUNUUID          _MSI_RECORD_CDCOUN lis         _MSI_RECDCOUN    ize+BA  N   _MSI_RECORD_CDCOUNs     THODDEFTINEL };

static PyTypeObject record   chimpl   COTFI"Docrderimpl( bject recordord_Typmetcabna]
 _imp cabnaTFIELmetcabna]
 "_msi.Rec,p_name.erfOperimpl   , -1, impl_MSI_RE } else {
 e {
 e {
 eObjectmetOD.Rec     LmeI   _name((msiesult = Pyonst char* ong_FromLef(filtcabna_eplaced,_imp cabnan= INVALID_Hm    return PyErr_No
    return P);
    rcabna_AddIntC as dat y_TYPE(res &ca  mDB           DIRECT"st(
/*[c(SIZE_T)  mDB           DIRECT););
    rcabna_AddIntC as dat y_TYPE(res &ca  mDB           "st(
/*[c(SIZE_T)  mDB           ););
    rcabna_AddIntC as dat y_TYPE(res &ca  mDB     DIRECT"st(
/*[c(SIZE_T)  mDB     DIRECT););
    rcabna_AddIntC as dat y_TYPE(res &ca  mDB       OPO_NO"st(
/*[c(SIZE_T)  mDB       OPO_NO););
    rcabna_AddIntC as dat y_TYPE(res &ca  mDB     TRANSACT"st(
/*[c(SIZE_T)  mDB     TRANSACT););
    rcabna_AddIntC as dat y_TYPE(res &ca  mDB     PATCH
   "st(
/*[c(SIZE_T)  mDB     PATCH
    n P);
    rcabna_AddIntMacro(m,o  mCOL    _NAMES););
    rcabna_AddIntMacro(m,o  mCOL    _me);S n P);
    rcabna_AddIntMacro(m,o  mMODIFYaSEEK););
    rcabna_AddIntMacro(m,o  mMODIFYaREFRESH););
    rcabna_AddIntMacro(m,o  mMODIFYaINSERT););
    rcabna_AddIntMacro(m,o  mMODIFYaUPD   ););
    rcabna_AddIntMacro(m,o  mMODIFYaASSIGN););
    rcabna_AddIntMacro(m,o  mMODIFYaREPLAC ););
    rcabna_AddIntMacro(m,o  mMODIFYaMERG ););
    rcabna_AddIntMacro(m,o  mMODIFYaDELE  ););
    rcabna_AddIntMacro(m,o  mMODIFYaINSERT_TEMPORARY););
    rcabna_AddIntMacro(m,o  mMODIFYa        ););
    rcabna_AddIntMacro(m,o  mMODIFYa        _NEW););
    rcabna_AddIntMacro(m,o  mMODIFYa        _F, _M););
    rcabna_AddIntMacro(m,o  mMODIFYa        _DELE  );););
    rcabna_AddIntMacro(m,o  vaCODEPAG ););
    rcabna_AddIntMacro(m,o  vaTITL ););
    rcabna_AddIntMacro(m,o  vaSUBJECT););
    rcabna_AddIntMacro(m,o  vaAUNELR););
    rcabna_AddIntMacro(m,o  vaKEY(sbuS););
    rcabna_AddIntMacro(m,o  vaCOMMc PS););
    rcabna_AddIntMacro(m,o  vaTEMPL   ););
    rcabna_AddIntMacro(m,o  vaLASTAUNELR););
    rcabna_AddIntMacro(m,o  vaREVNUMBER););
    rcabna_AddIntMacro(m,o  vaLASTPR
   D););
    rcabna_AddIntMacro(m,o  vaC      DTM););
    rcabna_AddIntMacro(m,o  vaLASTSAV  DTM););
    rcabna_AddIntMacro(m,o  vaPAG SI_RE););
    rcabna_AddIntMacro(m,o  va(sbuSI_RE););
    rcabna_AddIntMacro(m,o  vacodeSI_RE););
    rcabna_AddIntMacro(m,o  vaAPPNAME););
    rcabna_AddIntMacro(m,o  vaSECURITY);););
  t converf(fil     viExceppl(l_name*t conver" } else {
        P_SUC t conver)LL;
    }
    return PyLon  rcabna_Addst cha( &ca  monver" }t conver);/_msf
  
 GIL DISABLED PyLon  Uas dbna_rcabna_SetGIL(m,o y_MOD GIL  OTFUS D););#end f_