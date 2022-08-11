// name - имя cookie
// value - значение cookie

function setCookie(name, value) {
        var curCookie = name + "=" + escape(value);
        document.cookie = curCookie;
}

// name - имя считываемого cookie

function getCookie(name) {
        var prefix = name + "="
        var cookieStartIndex = document.cookie.indexOf(prefix)
        if (cookieStartIndex == -1)
                return null
        var cookieEndIndex = document.cookie.indexOf(";", cookieStartIndex + prefix.length)
        if (cookieEndIndex == -1)
                cookieEndIndex = document.cookie.length
        return unescape(document.cookie.substring(cookieStartIndex + prefix.length, cookieEndIndex))
}

// name - имя cookie
function deleteCookie(name) {
        if (getCookie(name)) {
                document.cookie = name + "=" + "; expires=Thu, 01-Jan-70 00:00:01 GMT"
        }
}