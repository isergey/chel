var ts = "%D0%B1";
var term = "TERM_1";
var use = "USE_1";
var struct = "STRUCT_1";
var rel = "REL_1";
var cks = "zgate_selected";

if (navigator.userAgent.indexOf('Mozilla') >= 0) {
    s = navigator.userAgent.indexOf('rv:');
    e = navigator.userAgent.indexOf(')');
    rv = navigator.userAgent.substr((s + 3), (e - s - 3));
}

function showKeyboard() {
    window.open('/rvkl/', '', 'width=355, height=145, status=yes, resizable=1');
    return false;
}

function openDialog() {
    window.open('/JCDialog/JDialog.html', 'javaDialog', 'width=320, height=187, status=yes, resizable=1');
    return false;
}

function setCls(cls) {
    document.forms.ZGATE.elements[term].value = cls;
}

function appendCls(cls) {
    document.forms.ZGATE.elements[term].value += cls;
}

function setTerm(val) {
    term = val;
    var n = term.search('_');
    var x = term.substr(n);
    use = 'USE' + x;
    struct = 'STRUCT' + x;
    rel = 'REL' + x;
}

function setForm(x) {
    if (unescape(ts).length == 2 &&
        (!(navigator.userAgent.indexOf('Mozilla') >= 0 && rv >= '1.6')) || navigator.userAgent.indexOf('MSIE') >= 0)
        window.opener.setCls(decode_utf8(unescape(x)));
    else
        window.opener.setCls(x);
    this.close();
}

function showHoldings(f) {
    var i;

    with (f)
        if (elements.SHOW_HOLDINGS.checked) {
            for (i = 0; i < elements.RECSYNTAX.length; i++)
                if (elements.RECSYNTAX.options[i].value == "1.2.840.10003.5.102") {
                    elements.RECSYNTAX.selectedIndex = i;
                    break;
                }
        } else
            for (i = 0; i < elements.RECSYNTAX.length; i++)
                if (elements.RECSYNTAX.options[i].value != "1.2.840.10003.5.102") {
                    elements.RECSYNTAX.selectedIndex = i;
                    break;
                }
}

function recordSyntax(f) {
    with (f)
        if (elements.RECSYNTAX.options[elements.RECSYNTAX.selectedIndex].value == "1.2.840.10003.5.102")
            elements.SHOW_HOLDINGS.checked = true;
        else
            elements.SHOW_HOLDINGS.checked = false;
}

function showProgress(ref) {
    var y = window.screenY + window.outerHeight / 2 - 50;
    var x = window.screenX + window.outerWidth / 2 - 100;
    var s = 'width=200, height=100, top=' + y + ', left=' + x;
    w = window.open(ref, null, s);
}

function showDiagnostics() {
    var i;
    var divs = document.getElementsByTagName("div");
    var cl = 'class';
    if (navigator.userAgent.indexOf('MSIE') >= 0)
        cl = 'className';
    for (i = 0; i < divs.length; i++)
        if (divs[i].getAttribute(cl) == 'diag')
            divs[i].style.display = 'block';

    var x = document.getElementsByTagName("span");
    for (i = 0; i < x.length; i++)
        if (x[i].getAttribute(cl) == 'show_diag')
            x[i].style.display = 'none';
}

function scan(ref, db, attr, attrset) {
    var i;
    var fl = false;

    with (document.forms.ZGATE) {
        ref += '?zstate=action&ACTION=SCAN&SESSION_ID=';
        ref += elements.SESSION_ID.value;
        ref += '&DBNAME=';
        if (db == null) {
            if (elements.DBNAME.type == 'select-multiple') {
                for (i = 0; i < elements.DBNAME.length; i++)
                    if (elements.DBNAME.options[i].selected) {
                        if (fl)
                            ref += ',';
                        ref += elements.DBNAME.options[i].value;
                        fl = true;
                    }
            } else
                ref += elements.DBNAME.value;
        } else
            ref += db;
        if (elements.CHAR_SET) {
            ref += '&CHAR_SET=';
            ref += elements.CHAR_SET.value;
        }
        ref += '&LANG=';
        ref += elements.LANG.value;
        if (elements.STEP_SIZE) {
            ref += '&STEP_SIZE=';
            ref += elements.STEP_SIZE.value;
        }
        if (elements.PREF_POS) {
            ref += '&PREF_POS=';
            ref += elements.PREF_POS.value;
        }
        ref += '&MAXRECORDS=';
        ref += elements.MAXRECORDS.value;
        if (elements.RECSYNTAX) {
            ref += '&RECSYNTAX=';
            ref += elements.RECSYNTAX.value;
        }
        if (attrset == null) {
            if (elements.ATTSET) {
                ref += '&ATTSET=';
                ref += elements.ATTSET.value;
            }
        } else {
            ref += '&ATTSET=';
            ref += attrset;
        }
        if (elements.SHOW_HOLDINGS) {
            ref += '&SHOW_HOLDINGS=';
            ref += elements.SHOW_HOLDINGS.value;
        }
        ref += '&' + use + '=';
        if (attr == null)
            ref += elements[use].value;
        else
            ref += attr;
        if (elements[rel]) {
            ref += '&' + rel + '=';
            ref += elements[rel].value;
        }
        if (elements[struct]) {
            ref += '&' + struct + '=';
            ref += elements[struct].value;
        }
        ref += '&' + term + '=';
        if (navigator.appName.indexOf('Netscape') >= 0 &&
            !(navigator.userAgent.indexOf('Mozilla') >= 0 && rv >= "1.6"))
            ref += escape(elements[term].value);
        else
            ref += escape(encode_utf8(elements[term].value));
    }
    window.open(ref, null);
}

function processSelected() {
    var i;
    var x;
    var r;
    var s = GetCookie(cks);

    if (s == null || s == '')
        return;
    var e = document.getElementsByName("sel");
    for (i = 0; i < e.length; i++) {
        x = '(^|:)' + e[i].id + '(:|$)';
        r = new RegExp(x, 'g');
        if (s.search(r) != -1)
            e[i].checked = true;
        else
            e[i].checked = false;
    }
}

function selectRecord(o) {
    if (o.checked)
        AppendCookie(cks, o.id);
    else
        CutFromCookie(cks, o.id);
}

function AppendCookie(name, value) {
    var s = GetCookie(name);
    if (s == null || s == '')
        s = value;
    else
        s += ':' + value;
    SetCookie(name, s, null, '/', null, null);
}

function CutFromCookie(name, value) {
    var s = GetCookie(name);
    var x = '(^|:)' + value + '(:|$)';
    var r1 = new RegExp(x, 'g');
    var r2 = new RegExp('^:|:$', 'g');
    if (s == null || s == '')
        return;
    s = s.replace(r1, ':');
    s = s.replace(r2, '');
    SetCookie(name, s, null, '/', null, null);
}

function getCookieVal(offset) {
    var endstr = document.cookie.indexOf(";", offset);
    if (endstr == -1)
        endstr = document.cookie.length;
    return unescape(document.cookie.substring(offset, endstr));
}

function GetCookie(name) {
    var arg = name + "=";
    var alen = arg.length;
    var clen = document.cookie.length;
    var i = 0;
    while (i < clen) {
        var j = i + alen;
        if (document.cookie.substring(i, j) == arg)
            return getCookieVal(j);
        i = document.cookie.indexOf(" ", i) + 1;
        if (i == 0)
            break;
    }
    return null;
}

function SetCookie(name, value, expires, path, domain, secure) {
    document.cookie = name + "=" + escape(value) +
        ((expires) ? "; expires=" + expires.toGMTString() : "") +
        ((path) ? "; path=" + path : "") +
        ((domain) ? "; domain=" + domain : "") +
        ((secure) ? "; secure" : "");
}

function decode_utf8(u) {
    var p = "";
    var i = 0;
    var c = c1 = c2 = 0;
    while (i < u.length) {
        c = u.charCodeAt(i);
        if (c < 128) {
            p += String.fromCharCode(c);
            i++;
        } else if ((c > 191) && (c < 224)) {
            c2 = u.charCodeAt(i + 1);
            p += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
            i += 2;
        } else {
            c2 = u.charCodeAt(i + 1);
            c3 = u.charCodeAt(i + 2);
            p += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
            i += 3;
        }
    }
    return p;
}

function encode_utf8(t) {
    t = t.replace(/\r\n/g, "\n");
    var u = "";
    for (var n = 0; n < t.length; n++) {
        var c = t.charCodeAt(n);
        if (c < 128)
            u += String.fromCharCode(c);
        else if ((c > 127) && (c < 2048)) {
            u += String.fromCharCode((c >> 6) | 192);
            u += String.fromCharCode((c & 63) | 128);
        } else {
            u += String.fromCharCode((c >> 12) | 224);
            u += String.fromCharCode(((c >> 6) & 63) | 128);
            u += String.fromCharCode((c & 63) | 128);
        }
    }
    return u;
}

function selectOptions(value) {
    var cl = 'class';
    if (navigator.userAgent.indexOf('MSIE') >= 0)
        cl = 'className';

    with (document.forms.ZGATE) {
        if (elements.DBNAME.type == 'select-multiple')
            for (i = 0; i < elements.DBNAME.length; i++) {
                elements.DBNAME.options[i].selected = true;
                if (elements.DBNAME.options[i].getAttribute(cl) < value)
                    elements.DBNAME.options[i].selected = false;
            }
    }
}