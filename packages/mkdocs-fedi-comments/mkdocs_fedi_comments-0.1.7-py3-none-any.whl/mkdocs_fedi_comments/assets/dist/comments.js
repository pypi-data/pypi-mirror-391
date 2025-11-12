var me, w, ut, X, He, ct, _t, lt, Oe, we, ke, oe = {}, ft = [], Pt = /acit|ex(?:s|g|n|p|$)|rph|grid|ows|mnc|ntw|ine[ch]|zoo|^ord|itera/i, ie = Array.isArray;
function Y(e, t) {
  for (var r in t) e[r] = t[r];
  return e;
}
function Ce(e) {
  e && e.parentNode && e.parentNode.removeChild(e);
}
function Ae(e, t, r) {
  var n, o, i, s = {};
  for (i in t) i == "key" ? n = t[i] : i == "ref" ? o = t[i] : s[i] = t[i];
  if (arguments.length > 2 && (s.children = arguments.length > 3 ? me.call(arguments, 2) : r), typeof e == "function" && e.defaultProps != null) for (i in e.defaultProps) s[i] === void 0 && (s[i] = e.defaultProps[i]);
  return _e(e, s, n, o, null);
}
function _e(e, t, r, n, o) {
  var i = { type: e, props: t, key: r, ref: n, __k: null, __: null, __b: 0, __e: null, __c: null, constructor: void 0, __v: o ?? ++ut, __i: -1, __u: 0 };
  return o == null && w.vnode != null && w.vnode(i), i;
}
function W(e) {
  return e.children;
}
function G(e, t) {
  this.props = e, this.context = t;
}
function te(e, t) {
  if (t == null) return e.__ ? te(e.__, e.__i + 1) : null;
  for (var r; t < e.__k.length; t++) if ((r = e.__k[t]) != null && r.__e != null) return r.__e;
  return typeof e.type == "function" ? te(e) : null;
}
function dt(e) {
  var t, r;
  if ((e = e.__) != null && e.__c != null) {
    for (e.__e = e.__c.base = null, t = 0; t < e.__k.length; t++) if ((r = e.__k[t]) != null && r.__e != null) {
      e.__e = e.__c.base = r.__e;
      break;
    }
    return dt(e);
  }
}
function Pe(e) {
  (!e.__d && (e.__d = !0) && X.push(e) && !de.__r++ || He != w.debounceRendering) && ((He = w.debounceRendering) || ct)(de);
}
function de() {
  for (var e, t, r, n, o, i, s, a = 1; X.length; ) X.length > a && X.sort(_t), e = X.shift(), a = X.length, e.__d && (r = void 0, n = void 0, o = (n = (t = e).__v).__e, i = [], s = [], t.__P && ((r = Y({}, n)).__v = n.__v + 1, w.vnode && w.vnode(r), Ie(t.__P, r, n, t.__n, t.__P.namespaceURI, 32 & n.__u ? [o] : null, i, o ?? te(n), !!(32 & n.__u), s), r.__v = n.__v, r.__.__k[r.__i] = r, mt(i, r, s), n.__e = n.__ = null, r.__e != o && dt(r)));
  de.__r = 0;
}
function ht(e, t, r, n, o, i, s, a, _, c, l) {
  var u, v, p, M, b, S, A, x = n && n.__k || ft, P = t.length;
  for (_ = Tt(r, t, x, _, P), u = 0; u < P; u++) (p = r.__k[u]) != null && (v = p.__i == -1 ? oe : x[p.__i] || oe, p.__i = u, S = Ie(e, p, v, o, i, s, a, _, c, l), M = p.__e, p.ref && v.ref != p.ref && (v.ref && Ee(v.ref, null, p), l.push(p.ref, p.__c || M, p)), b == null && M != null && (b = M), (A = !!(4 & p.__u)) || v.__k === p.__k ? _ = pt(p, _, e, A) : typeof p.type == "function" && S !== void 0 ? _ = S : M && (_ = M.nextSibling), p.__u &= -7);
  return r.__e = b, _;
}
function Tt(e, t, r, n, o) {
  var i, s, a, _, c, l = r.length, u = l, v = 0;
  for (e.__k = new Array(o), i = 0; i < o; i++) (s = t[i]) != null && typeof s != "boolean" && typeof s != "function" ? (_ = i + v, (s = e.__k[i] = typeof s == "string" || typeof s == "number" || typeof s == "bigint" || s.constructor == String ? _e(null, s, null, null, null) : ie(s) ? _e(W, { children: s }, null, null, null) : s.constructor == null && s.__b > 0 ? _e(s.type, s.props, s.key, s.ref ? s.ref : null, s.__v) : s).__ = e, s.__b = e.__b + 1, a = null, (c = s.__i = Ut(s, r, _, u)) != -1 && (u--, (a = r[c]) && (a.__u |= 2)), a == null || a.__v == null ? (c == -1 && (o > l ? v-- : o < l && v++), typeof s.type != "function" && (s.__u |= 4)) : c != _ && (c == _ - 1 ? v-- : c == _ + 1 ? v++ : (c > _ ? v-- : v++, s.__u |= 4))) : e.__k[i] = null;
  if (u) for (i = 0; i < l; i++) (a = r[i]) != null && (2 & a.__u) == 0 && (a.__e == n && (n = te(a)), vt(a, a));
  return n;
}
function pt(e, t, r, n) {
  var o, i;
  if (typeof e.type == "function") {
    for (o = e.__k, i = 0; o && i < o.length; i++) o[i] && (o[i].__ = e, t = pt(o[i], t, r, n));
    return t;
  }
  e.__e != t && (n && (t && e.type && !t.parentNode && (t = te(e)), r.insertBefore(e.__e, t || null)), t = e.__e);
  do
    t = t && t.nextSibling;
  while (t != null && t.nodeType == 8);
  return t;
}
function he(e, t) {
  return t = t || [], e == null || typeof e == "boolean" || (ie(e) ? e.some(function(r) {
    he(r, t);
  }) : t.push(e)), t;
}
function Ut(e, t, r, n) {
  var o, i, s, a = e.key, _ = e.type, c = t[r], l = c != null && (2 & c.__u) == 0;
  if (c === null && e.key == null || l && a == c.key && _ == c.type) return r;
  if (n > (l ? 1 : 0)) {
    for (o = r - 1, i = r + 1; o >= 0 || i < t.length; ) if ((c = t[s = o >= 0 ? o-- : i++]) != null && (2 & c.__u) == 0 && a == c.key && _ == c.type) return s;
  }
  return -1;
}
function Te(e, t, r) {
  t[0] == "-" ? e.setProperty(t, r ?? "") : e[t] = r == null ? "" : typeof r != "number" || Pt.test(t) ? r : r + "px";
}
function ue(e, t, r, n, o) {
  var i, s;
  e: if (t == "style") if (typeof r == "string") e.style.cssText = r;
  else {
    if (typeof n == "string" && (e.style.cssText = n = ""), n) for (t in n) r && t in r || Te(e.style, t, "");
    if (r) for (t in r) n && r[t] == n[t] || Te(e.style, t, r[t]);
  }
  else if (t[0] == "o" && t[1] == "n") i = t != (t = t.replace(lt, "$1")), s = t.toLowerCase(), t = s in e || t == "onFocusOut" || t == "onFocusIn" ? s.slice(2) : t.slice(2), e.l || (e.l = {}), e.l[t + i] = r, r ? n ? r.u = n.u : (r.u = Oe, e.addEventListener(t, i ? ke : we, i)) : e.removeEventListener(t, i ? ke : we, i);
  else {
    if (o == "http://www.w3.org/2000/svg") t = t.replace(/xlink(H|:h)/, "h").replace(/sName$/, "s");
    else if (t != "width" && t != "height" && t != "href" && t != "list" && t != "form" && t != "tabIndex" && t != "download" && t != "rowSpan" && t != "colSpan" && t != "role" && t != "popover" && t in e) try {
      e[t] = r ?? "";
      break e;
    } catch {
    }
    typeof r == "function" || (r == null || r === !1 && t[4] != "-" ? e.removeAttribute(t) : e.setAttribute(t, t == "popover" && r == 1 ? "" : r));
  }
}
function Ue(e) {
  return function(t) {
    if (this.l) {
      var r = this.l[t.type + e];
      if (t.t == null) t.t = Oe++;
      else if (t.t < r.u) return;
      return r(w.event ? w.event(t) : t);
    }
  };
}
function Ie(e, t, r, n, o, i, s, a, _, c) {
  var l, u, v, p, M, b, S, A, x, P, C, D, O, j, B, F, H, k = t.type;
  if (t.constructor != null) return null;
  128 & r.__u && (_ = !!(32 & r.__u), i = [a = t.__e = r.__e]), (l = w.__b) && l(t);
  e: if (typeof k == "function") try {
    if (A = t.props, x = "prototype" in k && k.prototype.render, P = (l = k.contextType) && n[l.__c], C = l ? P ? P.props.value : l.__ : n, r.__c ? S = (u = t.__c = r.__c).__ = u.__E : (x ? t.__c = u = new k(A, C) : (t.__c = u = new G(A, C), u.constructor = k, u.render = Nt), P && P.sub(u), u.props = A, u.state || (u.state = {}), u.context = C, u.__n = n, v = u.__d = !0, u.__h = [], u._sb = []), x && u.__s == null && (u.__s = u.state), x && k.getDerivedStateFromProps != null && (u.__s == u.state && (u.__s = Y({}, u.__s)), Y(u.__s, k.getDerivedStateFromProps(A, u.__s))), p = u.props, M = u.state, u.__v = t, v) x && k.getDerivedStateFromProps == null && u.componentWillMount != null && u.componentWillMount(), x && u.componentDidMount != null && u.__h.push(u.componentDidMount);
    else {
      if (x && k.getDerivedStateFromProps == null && A !== p && u.componentWillReceiveProps != null && u.componentWillReceiveProps(A, C), !u.__e && u.shouldComponentUpdate != null && u.shouldComponentUpdate(A, u.__s, C) === !1 || t.__v == r.__v) {
        for (t.__v != r.__v && (u.props = A, u.state = u.__s, u.__d = !1), t.__e = r.__e, t.__k = r.__k, t.__k.some(function(q) {
          q && (q.__ = t);
        }), D = 0; D < u._sb.length; D++) u.__h.push(u._sb[D]);
        u._sb = [], u.__h.length && s.push(u);
        break e;
      }
      u.componentWillUpdate != null && u.componentWillUpdate(A, u.__s, C), x && u.componentDidUpdate != null && u.__h.push(function() {
        u.componentDidUpdate(p, M, b);
      });
    }
    if (u.context = C, u.props = A, u.__P = e, u.__e = !1, O = w.__r, j = 0, x) {
      for (u.state = u.__s, u.__d = !1, O && O(t), l = u.render(u.props, u.state, u.context), B = 0; B < u._sb.length; B++) u.__h.push(u._sb[B]);
      u._sb = [];
    } else do
      u.__d = !1, O && O(t), l = u.render(u.props, u.state, u.context), u.state = u.__s;
    while (u.__d && ++j < 25);
    u.state = u.__s, u.getChildContext != null && (n = Y(Y({}, n), u.getChildContext())), x && !v && u.getSnapshotBeforeUpdate != null && (b = u.getSnapshotBeforeUpdate(p, M)), F = l, l != null && l.type === W && l.key == null && (F = yt(l.props.children)), a = ht(e, ie(F) ? F : [F], t, r, n, o, i, s, a, _, c), u.base = t.__e, t.__u &= -161, u.__h.length && s.push(u), S && (u.__E = u.__ = null);
  } catch (q) {
    if (t.__v = null, _ || i != null) if (q.then) {
      for (t.__u |= _ ? 160 : 128; a && a.nodeType == 8 && a.nextSibling; ) a = a.nextSibling;
      i[i.indexOf(a)] = null, t.__e = a;
    } else {
      for (H = i.length; H--; ) Ce(i[H]);
      Se(t);
    }
    else t.__e = r.__e, t.__k = r.__k, q.then || Se(t);
    w.__e(q, t, r);
  }
  else i == null && t.__v == r.__v ? (t.__k = r.__k, t.__e = r.__e) : a = t.__e = jt(r.__e, t, r, n, o, i, s, _, c);
  return (l = w.diffed) && l(t), 128 & t.__u ? void 0 : a;
}
function Se(e) {
  e && e.__c && (e.__c.__e = !0), e && e.__k && e.__k.forEach(Se);
}
function mt(e, t, r) {
  for (var n = 0; n < r.length; n++) Ee(r[n], r[++n], r[++n]);
  w.__c && w.__c(t, e), e.some(function(o) {
    try {
      e = o.__h, o.__h = [], e.some(function(i) {
        i.call(o);
      });
    } catch (i) {
      w.__e(i, o.__v);
    }
  });
}
function yt(e) {
  return typeof e != "object" || e == null || e.__b && e.__b > 0 ? e : ie(e) ? e.map(yt) : Y({}, e);
}
function jt(e, t, r, n, o, i, s, a, _) {
  var c, l, u, v, p, M, b, S = r.props, A = t.props, x = t.type;
  if (x == "svg" ? o = "http://www.w3.org/2000/svg" : x == "math" ? o = "http://www.w3.org/1998/Math/MathML" : o || (o = "http://www.w3.org/1999/xhtml"), i != null) {
    for (c = 0; c < i.length; c++) if ((p = i[c]) && "setAttribute" in p == !!x && (x ? p.localName == x : p.nodeType == 3)) {
      e = p, i[c] = null;
      break;
    }
  }
  if (e == null) {
    if (x == null) return document.createTextNode(A);
    e = document.createElementNS(o, x, A.is && A), a && (w.__m && w.__m(t, i), a = !1), i = null;
  }
  if (x == null) S === A || a && e.data == A || (e.data = A);
  else {
    if (i = i && me.call(e.childNodes), S = r.props || oe, !a && i != null) for (S = {}, c = 0; c < e.attributes.length; c++) S[(p = e.attributes[c]).name] = p.value;
    for (c in S) if (p = S[c], c != "children") {
      if (c == "dangerouslySetInnerHTML") u = p;
      else if (!(c in A)) {
        if (c == "value" && "defaultValue" in A || c == "checked" && "defaultChecked" in A) continue;
        ue(e, c, null, p, o);
      }
    }
    for (c in A) p = A[c], c == "children" ? v = p : c == "dangerouslySetInnerHTML" ? l = p : c == "value" ? M = p : c == "checked" ? b = p : a && typeof p != "function" || S[c] === p || ue(e, c, p, S[c], o);
    if (l) a || u && (l.__html == u.__html || l.__html == e.innerHTML) || (e.innerHTML = l.__html), t.__k = [];
    else if (u && (e.innerHTML = ""), ht(t.type == "template" ? e.content : e, ie(v) ? v : [v], t, r, n, x == "foreignObject" ? "http://www.w3.org/1999/xhtml" : o, i, s, i ? i[0] : r.__k && te(r, 0), a, _), i != null) for (c = i.length; c--; ) Ce(i[c]);
    a || (c = "value", x == "progress" && M == null ? e.removeAttribute("value") : M != null && (M !== e[c] || x == "progress" && !M || x == "option" && M != S[c]) && ue(e, c, M, S[c], o), c = "checked", b != null && b != e[c] && ue(e, c, b, S[c], o));
  }
  return e;
}
function Ee(e, t, r) {
  try {
    if (typeof e == "function") {
      var n = typeof e.__u == "function";
      n && e.__u(), n && t == null || (e.__u = e(t));
    } else e.current = t;
  } catch (o) {
    w.__e(o, r);
  }
}
function vt(e, t, r) {
  var n, o;
  if (w.unmount && w.unmount(e), (n = e.ref) && (n.current && n.current != e.__e || Ee(n, null, t)), (n = e.__c) != null) {
    if (n.componentWillUnmount) try {
      n.componentWillUnmount();
    } catch (i) {
      w.__e(i, t);
    }
    n.base = n.__P = null;
  }
  if (n = e.__k) for (o = 0; o < n.length; o++) n[o] && vt(n[o], t, r || typeof e.type != "function");
  r || Ce(e.__e), e.__c = e.__ = e.__e = void 0;
}
function Nt(e, t, r) {
  return this.constructor(e, r);
}
function gt(e, t, r) {
  var n, o, i, s;
  t == document && (t = document.documentElement), w.__ && w.__(e, t), o = (n = !1) ? null : t.__k, i = [], s = [], Ie(t, e = t.__k = Ae(W, null, [e]), o || oe, oe, t.namespaceURI, o ? null : t.firstChild ? me.call(t.childNodes) : null, i, o ? o.__e : t.firstChild, n, s), mt(i, e, s);
}
me = ft.slice, w = { __e: function(e, t, r, n) {
  for (var o, i, s; t = t.__; ) if ((o = t.__c) && !o.__) try {
    if ((i = o.constructor) && i.getDerivedStateFromError != null && (o.setState(i.getDerivedStateFromError(e)), s = o.__d), o.componentDidCatch != null && (o.componentDidCatch(e, n || {}), s = o.__d), s) return o.__E = o;
  } catch (a) {
    e = a;
  }
  throw e;
} }, ut = 0, G.prototype.setState = function(e, t) {
  var r;
  r = this.__s != null && this.__s != this.state ? this.__s : this.__s = Y({}, this.state), typeof e == "function" && (e = e(Y({}, r), this.props)), e && Y(r, e), e != null && this.__v && (t && this._sb.push(t), Pe(this));
}, G.prototype.forceUpdate = function(e) {
  this.__v && (this.__e = !0, e && this.__h.push(e), Pe(this));
}, G.prototype.render = W, X = [], ct = typeof Promise == "function" ? Promise.prototype.then.bind(Promise.resolve()) : setTimeout, _t = function(e, t) {
  return e.__v.__b - t.__v.__b;
}, de.__r = 0, lt = /(PointerCapture)$|Capture$/i, Oe = 0, we = Ue(!1), ke = Ue(!0);
var zt = 0;
function V(e, t, r, n, o, i) {
  t || (t = {});
  var s, a, _ = t;
  if ("ref" in _) for (a in _ = {}, t) a == "ref" ? s = t[a] : _[a] = t[a];
  var c = { type: e, props: _, key: r, ref: s, __k: null, __: null, __b: 0, __e: null, __c: null, constructor: void 0, __v: --zt, __i: -1, __u: 0, __source: o, __self: i };
  if (typeof e == "function" && (s = e.defaultProps)) for (a in s) _[a] === void 0 && (_[a] = s[a]);
  return w.vnode && w.vnode(c), c;
}
var pe, U, ge, je, xe = 0, bt = [], N = w, Ne = N.__b, ze = N.__r, Be = N.diffed, Re = N.__c, We = N.unmount, qe = N.__;
function $t(e, t) {
  N.__h && N.__h(U, e, xe || t), xe = 0;
  var r = U.__H || (U.__H = { __: [], __h: [] });
  return e >= r.__.length && r.__.push({}), r.__[e];
}
function Le(e) {
  return xe = 1, Bt(wt, e);
}
function Bt(e, t, r) {
  var n = $t(pe++, 2);
  if (n.t = e, !n.__c && (n.__ = [r ? r(t) : wt(void 0, t), function(a) {
    var _ = n.__N ? n.__N[0] : n.__[0], c = n.t(_, a);
    _ !== c && (n.__N = [c, n.__[1]], n.__c.setState({}));
  }], n.__c = U, !U.__f)) {
    var o = function(a, _, c) {
      if (!n.__c.__H) return !0;
      var l = n.__c.__H.__.filter(function(v) {
        return !!v.__c;
      });
      if (l.every(function(v) {
        return !v.__N;
      })) return !i || i.call(this, a, _, c);
      var u = n.__c.props !== a;
      return l.forEach(function(v) {
        if (v.__N) {
          var p = v.__[0];
          v.__ = v.__N, v.__N = void 0, p !== v.__[0] && (u = !0);
        }
      }), i && i.call(this, a, _, c) || u;
    };
    U.__f = !0;
    var i = U.shouldComponentUpdate, s = U.componentWillUpdate;
    U.componentWillUpdate = function(a, _, c) {
      if (this.__e) {
        var l = i;
        i = void 0, o(a, _, c), i = l;
      }
      s && s.call(this, a, _, c);
    }, U.shouldComponentUpdate = o;
  }
  return n.__N || n.__;
}
function Rt(e, t) {
  var r = $t(pe++, 3);
  !N.__s && Lt(r.__H, t) && (r.__ = e, r.u = t, U.__H.__h.push(r));
}
function Wt() {
  for (var e; e = bt.shift(); ) if (e.__P && e.__H) try {
    e.__H.__h.forEach(le), e.__H.__h.forEach(De), e.__H.__h = [];
  } catch (t) {
    e.__H.__h = [], N.__e(t, e.__v);
  }
}
N.__b = function(e) {
  U = null, Ne && Ne(e);
}, N.__ = function(e, t) {
  e && t.__k && t.__k.__m && (e.__m = t.__k.__m), qe && qe(e, t);
}, N.__r = function(e) {
  ze && ze(e), pe = 0;
  var t = (U = e.__c).__H;
  t && (ge === U ? (t.__h = [], U.__h = [], t.__.forEach(function(r) {
    r.__N && (r.__ = r.__N), r.u = r.__N = void 0;
  })) : (t.__h.forEach(le), t.__h.forEach(De), t.__h = [], pe = 0)), ge = U;
}, N.diffed = function(e) {
  Be && Be(e);
  var t = e.__c;
  t && t.__H && (t.__H.__h.length && (bt.push(t) !== 1 && je === N.requestAnimationFrame || ((je = N.requestAnimationFrame) || qt)(Wt)), t.__H.__.forEach(function(r) {
    r.u && (r.__H = r.u), r.u = void 0;
  })), ge = U = null;
}, N.__c = function(e, t) {
  t.some(function(r) {
    try {
      r.__h.forEach(le), r.__h = r.__h.filter(function(n) {
        return !n.__ || De(n);
      });
    } catch (n) {
      t.some(function(o) {
        o.__h && (o.__h = []);
      }), t = [], N.__e(n, r.__v);
    }
  }), Re && Re(e, t);
}, N.unmount = function(e) {
  We && We(e);
  var t, r = e.__c;
  r && r.__H && (r.__H.__.forEach(function(n) {
    try {
      le(n);
    } catch (o) {
      t = o;
    }
  }), r.__H = void 0, t && N.__e(t, r.__v));
};
var Fe = typeof requestAnimationFrame == "function";
function qt(e) {
  var t, r = function() {
    clearTimeout(n), Fe && cancelAnimationFrame(t), setTimeout(e);
  }, n = setTimeout(r, 35);
  Fe && (t = requestAnimationFrame(r));
}
function le(e) {
  var t = U, r = e.__c;
  typeof r == "function" && (e.__c = void 0, r()), U = t;
}
function De(e) {
  var t = U;
  e.__c = e.__(), U = t;
}
function Lt(e, t) {
  return !e || e.length !== t.length || t.some(function(r, n) {
    return r !== e[n];
  });
}
function wt(e, t) {
  return typeof t == "function" ? t(e) : t;
}
function Ft(e, t) {
  for (var r in t) e[r] = t[r];
  return e;
}
function Ve(e, t) {
  for (var r in e) if (r !== "__source" && !(r in t)) return !0;
  for (var n in t) if (n !== "__source" && e[n] !== t[n]) return !0;
  return !1;
}
function Qe(e, t) {
  this.props = e, this.context = t;
}
(Qe.prototype = new G()).isPureReactComponent = !0, Qe.prototype.shouldComponentUpdate = function(e, t) {
  return Ve(this.props, e) || Ve(this.state, t);
};
var Ye = w.__b;
w.__b = function(e) {
  e.type && e.type.__f && e.ref && (e.props.ref = e.ref, e.ref = null), Ye && Ye(e);
};
var Vt = w.__e;
w.__e = function(e, t, r, n) {
  if (e.then) {
    for (var o, i = t; i = i.__; ) if ((o = i.__c) && o.__c) return t.__e == null && (t.__e = r.__e, t.__k = r.__k), o.__c(e, t);
  }
  Vt(e, t, r, n);
};
var Ge = w.unmount;
function kt(e, t, r) {
  return e && (e.__c && e.__c.__H && (e.__c.__H.__.forEach(function(n) {
    typeof n.__c == "function" && n.__c();
  }), e.__c.__H = null), (e = Ft({}, e)).__c != null && (e.__c.__P === r && (e.__c.__P = t), e.__c.__e = !0, e.__c = null), e.__k = e.__k && e.__k.map(function(n) {
    return kt(n, t, r);
  })), e;
}
function At(e, t, r) {
  return e && r && (e.__v = null, e.__k = e.__k && e.__k.map(function(n) {
    return At(n, t, r);
  }), e.__c && e.__c.__P === t && (e.__e && r.appendChild(e.__e), e.__c.__e = !0, e.__c.__P = r)), e;
}
function be() {
  this.__u = 0, this.o = null, this.__b = null;
}
function St(e) {
  var t = e.__.__c;
  return t && t.__a && t.__a(e);
}
function ce() {
  this.i = null, this.l = null;
}
w.unmount = function(e) {
  var t = e.__c;
  t && t.__R && t.__R(), t && 32 & e.__u && (e.type = null), Ge && Ge(e);
}, (be.prototype = new G()).__c = function(e, t) {
  var r = t.__c, n = this;
  n.o == null && (n.o = []), n.o.push(r);
  var o = St(n.__v), i = !1, s = function() {
    i || (i = !0, r.__R = null, o ? o(a) : a());
  };
  r.__R = s;
  var a = function() {
    if (!--n.__u) {
      if (n.state.__a) {
        var _ = n.state.__a;
        n.__v.__k[0] = At(_, _.__c.__P, _.__c.__O);
      }
      var c;
      for (n.setState({ __a: n.__b = null }); c = n.o.pop(); ) c.forceUpdate();
    }
  };
  n.__u++ || 32 & t.__u || n.setState({ __a: n.__b = n.__v.__k[0] }), e.then(s, s);
}, be.prototype.componentWillUnmount = function() {
  this.o = [];
}, be.prototype.render = function(e, t) {
  if (this.__b) {
    if (this.__v.__k) {
      var r = document.createElement("div"), n = this.__v.__k[0].__c;
      this.__v.__k[0] = kt(this.__b, r, n.__O = n.__P);
    }
    this.__b = null;
  }
  var o = t.__a && Ae(W, null, e.fallback);
  return o && (o.__u &= -33), [Ae(W, null, t.__a ? null : e.children), o];
};
var Je = function(e, t, r) {
  if (++r[1] === r[0] && e.l.delete(t), e.props.revealOrder && (e.props.revealOrder[0] !== "t" || !e.l.size)) for (r = e.i; r; ) {
    for (; r.length > 3; ) r.pop()();
    if (r[1] < r[0]) break;
    e.i = r = r[2];
  }
};
(ce.prototype = new G()).__a = function(e) {
  var t = this, r = St(t.__v), n = t.l.get(e);
  return n[0]++, function(o) {
    var i = function() {
      t.props.revealOrder ? (n.push(o), Je(t, e, n)) : o();
    };
    r ? r(i) : i();
  };
}, ce.prototype.render = function(e) {
  this.i = null, this.l = /* @__PURE__ */ new Map();
  var t = he(e.children);
  e.revealOrder && e.revealOrder[0] === "b" && t.reverse();
  for (var r = t.length; r--; ) this.l.set(t[r], this.i = [1, 0, this.i]);
  return e.children;
}, ce.prototype.componentDidUpdate = ce.prototype.componentDidMount = function() {
  var e = this;
  this.l.forEach(function(t, r) {
    Je(e, r, t);
  });
};
var Qt = typeof Symbol < "u" && Symbol.for && Symbol.for("react.element") || 60103, Yt = /^(?:accent|alignment|arabic|baseline|cap|clip(?!PathU)|color|dominant|fill|flood|font|glyph(?!R)|horiz|image(!S)|letter|lighting|marker(?!H|W|U)|overline|paint|pointer|shape|stop|strikethrough|stroke|text(?!L)|transform|underline|unicode|units|v|vector|vert|word|writing|x(?!C))[A-Z]/, Gt = /^on(Ani|Tra|Tou|BeforeInp|Compo)/, Jt = /[A-Z0-9]/g, Zt = typeof document < "u", Kt = function(e) {
  return (typeof Symbol < "u" && typeof Symbol() == "symbol" ? /fil|che|rad/ : /fil|che|ra/).test(e);
};
function Xt(e, t, r) {
  return t.__k == null && (t.textContent = ""), gt(e, t), typeof r == "function" && r(), e ? e.__c : null;
}
G.prototype.isReactComponent = {}, ["componentWillMount", "componentWillReceiveProps", "componentWillUpdate"].forEach(function(e) {
  Object.defineProperty(G.prototype, e, { configurable: !0, get: function() {
    return this["UNSAFE_" + e];
  }, set: function(t) {
    Object.defineProperty(this, e, { configurable: !0, writable: !0, value: t });
  } });
});
var Ze = w.event;
function er() {
}
function tr() {
  return this.cancelBubble;
}
function rr() {
  return this.defaultPrevented;
}
w.event = function(e) {
  return Ze && (e = Ze(e)), e.persist = er, e.isPropagationStopped = tr, e.isDefaultPrevented = rr, e.nativeEvent = e;
};
var nr = { enumerable: !1, configurable: !0, get: function() {
  return this.class;
} }, Ke = w.vnode;
w.vnode = function(e) {
  typeof e.type == "string" && (function(t) {
    var r = t.props, n = t.type, o = {}, i = n.indexOf("-") === -1;
    for (var s in r) {
      var a = r[s];
      if (!(s === "value" && "defaultValue" in r && a == null || Zt && s === "children" && n === "noscript" || s === "class" || s === "className")) {
        var _ = s.toLowerCase();
        s === "defaultValue" && "value" in r && r.value == null ? s = "value" : s === "download" && a === !0 ? a = "" : _ === "translate" && a === "no" ? a = !1 : _[0] === "o" && _[1] === "n" ? _ === "ondoubleclick" ? s = "ondblclick" : _ !== "onchange" || n !== "input" && n !== "textarea" || Kt(r.type) ? _ === "onfocus" ? s = "onfocusin" : _ === "onblur" ? s = "onfocusout" : Gt.test(s) && (s = _) : _ = s = "oninput" : i && Yt.test(s) ? s = s.replace(Jt, "-$&").toLowerCase() : a === null && (a = void 0), _ === "oninput" && o[s = _] && (s = "oninputCapture"), o[s] = a;
      }
    }
    n == "select" && o.multiple && Array.isArray(o.value) && (o.value = he(r.children).forEach(function(c) {
      c.props.selected = o.value.indexOf(c.props.value) != -1;
    })), n == "select" && o.defaultValue != null && (o.value = he(r.children).forEach(function(c) {
      c.props.selected = o.multiple ? o.defaultValue.indexOf(c.props.value) != -1 : o.defaultValue == c.props.value;
    })), r.class && !r.className ? (o.class = r.class, Object.defineProperty(o, "className", nr)) : (r.className && !r.class || r.class && r.className) && (o.class = o.className = r.className), t.props = o;
  })(e), e.$$typeof = Qt, Ke && Ke(e);
};
var Xe = w.__r;
w.__r = function(e) {
  Xe && Xe(e), e.__c;
};
var et = w.diffed;
w.diffed = function(e) {
  et && et(e);
  var t = e.props, r = e.__e;
  r != null && e.type === "textarea" && "value" in t && t.value !== r.value && (r.value = t.value == null ? "" : t.value);
};
function or(e) {
  return !!e.__k && (gt(null, e), !0);
}
function ir(e) {
  return {
    // eslint-disable-next-line
    render: function(t) {
      Xt(t, e);
    },
    // eslint-disable-next-line
    unmount: function() {
      or(e);
    }
  };
}
const sr = {
  bodySerializer: (e) => JSON.stringify(
    e,
    (t, r) => typeof r == "bigint" ? r.toString() : r
  )
}, ar = ({
  onRequest: e,
  onSseError: t,
  onSseEvent: r,
  responseTransformer: n,
  responseValidator: o,
  sseDefaultRetryDelay: i,
  sseMaxRetryAttempts: s,
  sseMaxRetryDelay: a,
  sseSleepFn: _,
  url: c,
  ...l
}) => {
  let u;
  const v = _ ?? ((b) => new Promise((S) => setTimeout(S, b)));
  return { stream: async function* () {
    let b = i ?? 3e3, S = 0;
    const A = l.signal ?? new AbortController().signal;
    for (; !A.aborted; ) {
      S++;
      const x = l.headers instanceof Headers ? l.headers : new Headers(l.headers);
      u !== void 0 && x.set("Last-Event-ID", u);
      try {
        const P = {
          redirect: "follow",
          ...l,
          body: l.serializedBody,
          headers: x,
          signal: A
        };
        let C = new Request(c, P);
        e && (C = await e(c, P));
        const O = await (l.fetch ?? globalThis.fetch)(C);
        if (!O.ok)
          throw new Error(
            `SSE failed: ${O.status} ${O.statusText}`
          );
        if (!O.body) throw new Error("No body in SSE response");
        const j = O.body.pipeThrough(new TextDecoderStream()).getReader();
        let B = "";
        const F = () => {
          try {
            j.cancel();
          } catch {
          }
        };
        A.addEventListener("abort", F);
        try {
          for (; ; ) {
            const { done: H, value: k } = await j.read();
            if (H) break;
            B += k;
            const q = B.split(`

`);
            B = q.pop() ?? "";
            for (const se of q) {
              const g = se.split(`
`), d = [];
              let f;
              for (const y of g)
                if (y.startsWith("data:"))
                  d.push(y.replace(/^data:\s*/, ""));
                else if (y.startsWith("event:"))
                  f = y.replace(/^event:\s*/, "");
                else if (y.startsWith("id:"))
                  u = y.replace(/^id:\s*/, "");
                else if (y.startsWith("retry:")) {
                  const $ = Number.parseInt(
                    y.replace(/^retry:\s*/, ""),
                    10
                  );
                  Number.isNaN($) || (b = $);
                }
              let m, h = !1;
              if (d.length) {
                const y = d.join(`
`);
                try {
                  m = JSON.parse(y), h = !0;
                } catch {
                  m = y;
                }
              }
              h && (o && await o(m), n && (m = await n(m))), r?.({
                data: m,
                event: f,
                id: u,
                retry: b
              }), d.length && (yield m);
            }
          }
        } finally {
          A.removeEventListener("abort", F), j.releaseLock();
        }
        break;
      } catch (P) {
        if (t?.(P), s !== void 0 && S >= s)
          break;
        const C = Math.min(
          b * 2 ** (S - 1),
          a ?? 3e4
        );
        await v(C);
      }
    }
  }() };
}, ur = (e) => {
  switch (e) {
    case "label":
      return ".";
    case "matrix":
      return ";";
    case "simple":
      return ",";
    default:
      return "&";
  }
}, cr = (e) => {
  switch (e) {
    case "form":
      return ",";
    case "pipeDelimited":
      return "|";
    case "spaceDelimited":
      return "%20";
    default:
      return ",";
  }
}, _r = (e) => {
  switch (e) {
    case "label":
      return ".";
    case "matrix":
      return ";";
    case "simple":
      return ",";
    default:
      return "&";
  }
}, xt = ({
  allowReserved: e,
  explode: t,
  name: r,
  style: n,
  value: o
}) => {
  if (!t) {
    const a = (e ? o : o.map((_) => encodeURIComponent(_))).join(cr(n));
    switch (n) {
      case "label":
        return `.${a}`;
      case "matrix":
        return `;${r}=${a}`;
      case "simple":
        return a;
      default:
        return `${r}=${a}`;
    }
  }
  const i = ur(n), s = o.map((a) => n === "label" || n === "simple" ? e ? a : encodeURIComponent(a) : ye({
    allowReserved: e,
    name: r,
    value: a
  })).join(i);
  return n === "label" || n === "matrix" ? i + s : s;
}, ye = ({
  allowReserved: e,
  name: t,
  value: r
}) => {
  if (r == null)
    return "";
  if (typeof r == "object")
    throw new Error(
      "Deeply-nested arrays/objects aren’t supported. Provide your own `querySerializer()` to handle these."
    );
  return `${t}=${e ? r : encodeURIComponent(r)}`;
}, Dt = ({
  allowReserved: e,
  explode: t,
  name: r,
  style: n,
  value: o,
  valueOnly: i
}) => {
  if (o instanceof Date)
    return i ? o.toISOString() : `${r}=${o.toISOString()}`;
  if (n !== "deepObject" && !t) {
    let _ = [];
    Object.entries(o).forEach(([l, u]) => {
      _ = [
        ..._,
        l,
        e ? u : encodeURIComponent(u)
      ];
    });
    const c = _.join(",");
    switch (n) {
      case "form":
        return `${r}=${c}`;
      case "label":
        return `.${c}`;
      case "matrix":
        return `;${r}=${c}`;
      default:
        return c;
    }
  }
  const s = _r(n), a = Object.entries(o).map(
    ([_, c]) => ye({
      allowReserved: e,
      name: n === "deepObject" ? `${r}[${_}]` : _,
      value: c
    })
  ).join(s);
  return n === "label" || n === "matrix" ? s + a : a;
}, lr = /\{[^{}]+\}/g, fr = ({ path: e, url: t }) => {
  let r = t;
  const n = t.match(lr);
  if (n)
    for (const o of n) {
      let i = !1, s = o.substring(1, o.length - 1), a = "simple";
      s.endsWith("*") && (i = !0, s = s.substring(0, s.length - 1)), s.startsWith(".") ? (s = s.substring(1), a = "label") : s.startsWith(";") && (s = s.substring(1), a = "matrix");
      const _ = e[s];
      if (_ == null)
        continue;
      if (Array.isArray(_)) {
        r = r.replace(
          o,
          xt({ explode: i, name: s, style: a, value: _ })
        );
        continue;
      }
      if (typeof _ == "object") {
        r = r.replace(
          o,
          Dt({
            explode: i,
            name: s,
            style: a,
            value: _,
            valueOnly: !0
          })
        );
        continue;
      }
      if (a === "matrix") {
        r = r.replace(
          o,
          `;${ye({
            name: s,
            value: _
          })}`
        );
        continue;
      }
      const c = encodeURIComponent(
        a === "label" ? `.${_}` : _
      );
      r = r.replace(o, c);
    }
  return r;
}, dr = ({
  baseUrl: e,
  path: t,
  query: r,
  querySerializer: n,
  url: o
}) => {
  const i = o.startsWith("/") ? o : `/${o}`;
  let s = (e ?? "") + i;
  t && (s = fr({ path: t, url: s }));
  let a = r ? n(r) : "";
  return a.startsWith("?") && (a = a.substring(1)), a && (s += `?${a}`), s;
};
function hr(e) {
  const t = e.body !== void 0;
  if (t && e.bodySerializer)
    return "serializedBody" in e ? e.serializedBody !== void 0 && e.serializedBody !== "" ? e.serializedBody : null : e.body !== "" ? e.body : null;
  if (t)
    return e.body;
}
const pr = async (e, t) => {
  const r = typeof t == "function" ? await t(e) : t;
  if (r)
    return e.scheme === "bearer" ? `Bearer ${r}` : e.scheme === "basic" ? `Basic ${btoa(r)}` : r;
}, Mt = ({
  allowReserved: e,
  array: t,
  object: r
} = {}) => (o) => {
  const i = [];
  if (o && typeof o == "object")
    for (const s in o) {
      const a = o[s];
      if (a != null)
        if (Array.isArray(a)) {
          const _ = xt({
            allowReserved: e,
            explode: !0,
            name: s,
            style: "form",
            value: a,
            ...t
          });
          _ && i.push(_);
        } else if (typeof a == "object") {
          const _ = Dt({
            allowReserved: e,
            explode: !0,
            name: s,
            style: "deepObject",
            value: a,
            ...r
          });
          _ && i.push(_);
        } else {
          const _ = ye({
            allowReserved: e,
            name: s,
            value: a
          });
          _ && i.push(_);
        }
    }
  return i.join("&");
}, mr = (e) => {
  if (!e)
    return "stream";
  const t = e.split(";")[0]?.trim();
  if (t) {
    if (t.startsWith("application/json") || t.endsWith("+json"))
      return "json";
    if (t === "multipart/form-data")
      return "formData";
    if (["application/", "audio/", "image/", "video/"].some(
      (r) => t.startsWith(r)
    ))
      return "blob";
    if (t.startsWith("text/"))
      return "text";
  }
}, yr = (e, t) => t ? !!(e.headers.has(t) || e.query?.[t] || e.headers.get("Cookie")?.includes(`${t}=`)) : !1, vr = async ({
  security: e,
  ...t
}) => {
  for (const r of e) {
    if (yr(t, r.name))
      continue;
    const n = await pr(r, t.auth);
    if (!n)
      continue;
    const o = r.name ?? "Authorization";
    switch (r.in) {
      case "query":
        t.query || (t.query = {}), t.query[o] = n;
        break;
      case "cookie":
        t.headers.append("Cookie", `${o}=${n}`);
        break;
      case "header":
      default:
        t.headers.set(o, n);
        break;
    }
  }
}, tt = (e) => dr({
  baseUrl: e.baseUrl,
  path: e.path,
  query: e.query,
  querySerializer: typeof e.querySerializer == "function" ? e.querySerializer : Mt(e.querySerializer),
  url: e.url
}), rt = (e, t) => {
  const r = { ...e, ...t };
  return r.baseUrl?.endsWith("/") && (r.baseUrl = r.baseUrl.substring(0, r.baseUrl.length - 1)), r.headers = Ot(e.headers, t.headers), r;
}, gr = (e) => {
  const t = [];
  return e.forEach((r, n) => {
    t.push([n, r]);
  }), t;
}, Ot = (...e) => {
  const t = new Headers();
  for (const r of e) {
    if (!r)
      continue;
    const n = r instanceof Headers ? gr(r) : Object.entries(r);
    for (const [o, i] of n)
      if (i === null)
        t.delete(o);
      else if (Array.isArray(i))
        for (const s of i)
          t.append(o, s);
      else i !== void 0 && t.set(
        o,
        typeof i == "object" ? JSON.stringify(i) : i
      );
  }
  return t;
};
class $e {
  constructor() {
    this.fns = [];
  }
  clear() {
    this.fns = [];
  }
  eject(t) {
    const r = this.getInterceptorIndex(t);
    this.fns[r] && (this.fns[r] = null);
  }
  exists(t) {
    const r = this.getInterceptorIndex(t);
    return !!this.fns[r];
  }
  getInterceptorIndex(t) {
    return typeof t == "number" ? this.fns[t] ? t : -1 : this.fns.indexOf(t);
  }
  update(t, r) {
    const n = this.getInterceptorIndex(t);
    return this.fns[n] ? (this.fns[n] = r, t) : !1;
  }
  use(t) {
    return this.fns.push(t), this.fns.length - 1;
  }
}
const br = () => ({
  error: new $e(),
  request: new $e(),
  response: new $e()
}), $r = Mt({
  allowReserved: !1,
  array: {
    explode: !0,
    style: "form"
  },
  object: {
    explode: !0,
    style: "deepObject"
  }
}), wr = {
  "Content-Type": "application/json"
}, Ct = (e = {}) => ({
  ...sr,
  headers: wr,
  parseAs: "auto",
  querySerializer: $r,
  ...e
}), kr = (e = {}) => {
  let t = rt(Ct(), e);
  const r = () => ({ ...t }), n = (c) => (t = rt(t, c), r()), o = br(), i = async (c) => {
    const l = {
      ...t,
      ...c,
      fetch: c.fetch ?? t.fetch ?? globalThis.fetch,
      headers: Ot(t.headers, c.headers),
      serializedBody: void 0
    };
    l.security && await vr({
      ...l,
      security: l.security
    }), l.requestValidator && await l.requestValidator(l), l.body !== void 0 && l.bodySerializer && (l.serializedBody = l.bodySerializer(l.body)), (l.body === void 0 || l.serializedBody === "") && l.headers.delete("Content-Type");
    const u = tt(l);
    return { opts: l, url: u };
  }, s = async (c) => {
    const { opts: l, url: u } = await i(c), v = {
      redirect: "follow",
      ...l,
      body: hr(l)
    };
    let p = new Request(u, v);
    for (const D of o.request.fns)
      D && (p = await D(p, l));
    const M = l.fetch;
    let b = await M(p);
    for (const D of o.response.fns)
      D && (b = await D(b, p, l));
    const S = {
      request: p,
      response: b
    };
    if (b.ok) {
      const D = (l.parseAs === "auto" ? mr(b.headers.get("Content-Type")) : l.parseAs) ?? "json";
      if (b.status === 204 || b.headers.get("Content-Length") === "0") {
        let j;
        switch (D) {
          case "arrayBuffer":
          case "blob":
          case "text":
            j = await b[D]();
            break;
          case "formData":
            j = new FormData();
            break;
          case "stream":
            j = b.body;
            break;
          case "json":
          default:
            j = {};
            break;
        }
        return l.responseStyle === "data" ? j : {
          data: j,
          ...S
        };
      }
      let O;
      switch (D) {
        case "arrayBuffer":
        case "blob":
        case "formData":
        case "json":
        case "text":
          O = await b[D]();
          break;
        case "stream":
          return l.responseStyle === "data" ? b.body : {
            data: b.body,
            ...S
          };
      }
      return D === "json" && (l.responseValidator && await l.responseValidator(O), l.responseTransformer && (O = await l.responseTransformer(O))), l.responseStyle === "data" ? O : {
        data: O,
        ...S
      };
    }
    const A = await b.text();
    let x;
    try {
      x = JSON.parse(A);
    } catch {
    }
    const P = x ?? A;
    let C = P;
    for (const D of o.error.fns)
      D && (C = await D(P, b, p, l));
    if (C = C || {}, l.throwOnError)
      throw C;
    return l.responseStyle === "data" ? void 0 : {
      error: C,
      ...S
    };
  }, a = (c) => (l) => s({ ...l, method: c }), _ = (c) => async (l) => {
    const { opts: u, url: v } = await i(l);
    return ar({
      ...u,
      body: u.body,
      headers: u.headers,
      method: c,
      onRequest: async (p, M) => {
        let b = new Request(p, M);
        for (const S of o.request.fns)
          S && (b = await S(b, u));
        return b;
      },
      url: v
    });
  };
  return {
    buildUrl: tt,
    connect: a("CONNECT"),
    delete: a("DELETE"),
    get: a("GET"),
    getConfig: r,
    head: a("HEAD"),
    interceptors: o,
    options: a("OPTIONS"),
    patch: a("PATCH"),
    post: a("POST"),
    put: a("PUT"),
    request: s,
    setConfig: n,
    sse: {
      connect: _("CONNECT"),
      delete: _("DELETE"),
      get: _("GET"),
      head: _("HEAD"),
      options: _("OPTIONS"),
      patch: _("PATCH"),
      post: _("POST"),
      put: _("PUT"),
      trace: _("TRACE")
    },
    trace: a("TRACE")
  };
}, It = kr(Ct()), Ar = (e) => (e.client ?? It).get({
  url: "/{path}",
  ...e
});
function Sr(e) {
  return e && e.__esModule && Object.prototype.hasOwnProperty.call(e, "default") ? e.default : e;
}
var fe = { exports: {} }, xr = fe.exports, nt;
function Dr() {
  return nt || (nt = 1, (function(e, t) {
    (function(r, n) {
      e.exports = n();
    })(xr, (function() {
      var r = 1e3, n = 6e4, o = 36e5, i = "millisecond", s = "second", a = "minute", _ = "hour", c = "day", l = "week", u = "month", v = "quarter", p = "year", M = "date", b = "Invalid Date", S = /^(\d{4})[-/]?(\d{1,2})?[-/]?(\d{0,2})[Tt\s]*(\d{1,2})?:?(\d{1,2})?:?(\d{1,2})?[.:]?(\d+)?$/, A = /\[([^\]]+)]|Y{1,4}|M{1,4}|D{1,2}|d{1,4}|H{1,2}|h{1,2}|a|A|m{1,2}|s{1,2}|Z{1,2}|SSS/g, x = { name: "en", weekdays: "Sunday_Monday_Tuesday_Wednesday_Thursday_Friday_Saturday".split("_"), months: "January_February_March_April_May_June_July_August_September_October_November_December".split("_"), ordinal: function(g) {
        var d = ["th", "st", "nd", "rd"], f = g % 100;
        return "[" + g + (d[(f - 20) % 10] || d[f] || d[0]) + "]";
      } }, P = function(g, d, f) {
        var m = String(g);
        return !m || m.length >= d ? g : "" + Array(d + 1 - m.length).join(f) + g;
      }, C = { s: P, z: function(g) {
        var d = -g.utcOffset(), f = Math.abs(d), m = Math.floor(f / 60), h = f % 60;
        return (d <= 0 ? "+" : "-") + P(m, 2, "0") + ":" + P(h, 2, "0");
      }, m: function g(d, f) {
        if (d.date() < f.date()) return -g(f, d);
        var m = 12 * (f.year() - d.year()) + (f.month() - d.month()), h = d.clone().add(m, u), y = f - h < 0, $ = d.clone().add(m + (y ? -1 : 1), u);
        return +(-(m + (f - h) / (y ? h - $ : $ - h)) || 0);
      }, a: function(g) {
        return g < 0 ? Math.ceil(g) || 0 : Math.floor(g);
      }, p: function(g) {
        return { M: u, y: p, w: l, d: c, D: M, h: _, m: a, s, ms: i, Q: v }[g] || String(g || "").toLowerCase().replace(/s$/, "");
      }, u: function(g) {
        return g === void 0;
      } }, D = "en", O = {};
      O[D] = x;
      var j = "$isDayjsObject", B = function(g) {
        return g instanceof q || !(!g || !g[j]);
      }, F = function g(d, f, m) {
        var h;
        if (!d) return D;
        if (typeof d == "string") {
          var y = d.toLowerCase();
          O[y] && (h = y), f && (O[y] = f, h = y);
          var $ = d.split("-");
          if (!h && $.length > 1) return g($[0]);
        } else {
          var E = d.name;
          O[E] = d, h = E;
        }
        return !m && h && (D = h), h || !m && D;
      }, H = function(g, d) {
        if (B(g)) return g.clone();
        var f = typeof d == "object" ? d : {};
        return f.date = g, f.args = arguments, new q(f);
      }, k = C;
      k.l = F, k.i = B, k.w = function(g, d) {
        return H(g, { locale: d.$L, utc: d.$u, x: d.$x, $offset: d.$offset });
      };
      var q = (function() {
        function g(f) {
          this.$L = F(f.locale, null, !0), this.parse(f), this.$x = this.$x || f.x || {}, this[j] = !0;
        }
        var d = g.prototype;
        return d.parse = function(f) {
          this.$d = (function(m) {
            var h = m.date, y = m.utc;
            if (h === null) return /* @__PURE__ */ new Date(NaN);
            if (k.u(h)) return /* @__PURE__ */ new Date();
            if (h instanceof Date) return new Date(h);
            if (typeof h == "string" && !/Z$/i.test(h)) {
              var $ = h.match(S);
              if ($) {
                var E = $[2] - 1 || 0, T = ($[7] || "0").substring(0, 3);
                return y ? new Date(Date.UTC($[1], E, $[3] || 1, $[4] || 0, $[5] || 0, $[6] || 0, T)) : new Date($[1], E, $[3] || 1, $[4] || 0, $[5] || 0, $[6] || 0, T);
              }
            }
            return new Date(h);
          })(f), this.init();
        }, d.init = function() {
          var f = this.$d;
          this.$y = f.getFullYear(), this.$M = f.getMonth(), this.$D = f.getDate(), this.$W = f.getDay(), this.$H = f.getHours(), this.$m = f.getMinutes(), this.$s = f.getSeconds(), this.$ms = f.getMilliseconds();
        }, d.$utils = function() {
          return k;
        }, d.isValid = function() {
          return this.$d.toString() !== b;
        }, d.isSame = function(f, m) {
          var h = H(f);
          return this.startOf(m) <= h && h <= this.endOf(m);
        }, d.isAfter = function(f, m) {
          return H(f) < this.startOf(m);
        }, d.isBefore = function(f, m) {
          return this.endOf(m) < H(f);
        }, d.$g = function(f, m, h) {
          return k.u(f) ? this[m] : this.set(h, f);
        }, d.unix = function() {
          return Math.floor(this.valueOf() / 1e3);
        }, d.valueOf = function() {
          return this.$d.getTime();
        }, d.startOf = function(f, m) {
          var h = this, y = !!k.u(m) || m, $ = k.p(f), E = function(K, L) {
            var J = k.w(h.$u ? Date.UTC(h.$y, L, K) : new Date(h.$y, L, K), h);
            return y ? J : J.endOf(c);
          }, T = function(K, L) {
            return k.w(h.toDate()[K].apply(h.toDate("s"), (y ? [0, 0, 0, 0] : [23, 59, 59, 999]).slice(L)), h);
          }, z = this.$W, R = this.$M, Q = this.$D, ee = "set" + (this.$u ? "UTC" : "");
          switch ($) {
            case p:
              return y ? E(1, 0) : E(31, 11);
            case u:
              return y ? E(1, R) : E(0, R + 1);
            case l:
              var Z = this.$locale().weekStart || 0, re = (z < Z ? z + 7 : z) - Z;
              return E(y ? Q - re : Q + (6 - re), R);
            case c:
            case M:
              return T(ee + "Hours", 0);
            case _:
              return T(ee + "Minutes", 1);
            case a:
              return T(ee + "Seconds", 2);
            case s:
              return T(ee + "Milliseconds", 3);
            default:
              return this.clone();
          }
        }, d.endOf = function(f) {
          return this.startOf(f, !1);
        }, d.$set = function(f, m) {
          var h, y = k.p(f), $ = "set" + (this.$u ? "UTC" : ""), E = (h = {}, h[c] = $ + "Date", h[M] = $ + "Date", h[u] = $ + "Month", h[p] = $ + "FullYear", h[_] = $ + "Hours", h[a] = $ + "Minutes", h[s] = $ + "Seconds", h[i] = $ + "Milliseconds", h)[y], T = y === c ? this.$D + (m - this.$W) : m;
          if (y === u || y === p) {
            var z = this.clone().set(M, 1);
            z.$d[E](T), z.init(), this.$d = z.set(M, Math.min(this.$D, z.daysInMonth())).$d;
          } else E && this.$d[E](T);
          return this.init(), this;
        }, d.set = function(f, m) {
          return this.clone().$set(f, m);
        }, d.get = function(f) {
          return this[k.p(f)]();
        }, d.add = function(f, m) {
          var h, y = this;
          f = Number(f);
          var $ = k.p(m), E = function(R) {
            var Q = H(y);
            return k.w(Q.date(Q.date() + Math.round(R * f)), y);
          };
          if ($ === u) return this.set(u, this.$M + f);
          if ($ === p) return this.set(p, this.$y + f);
          if ($ === c) return E(1);
          if ($ === l) return E(7);
          var T = (h = {}, h[a] = n, h[_] = o, h[s] = r, h)[$] || 1, z = this.$d.getTime() + f * T;
          return k.w(z, this);
        }, d.subtract = function(f, m) {
          return this.add(-1 * f, m);
        }, d.format = function(f) {
          var m = this, h = this.$locale();
          if (!this.isValid()) return h.invalidDate || b;
          var y = f || "YYYY-MM-DDTHH:mm:ssZ", $ = k.z(this), E = this.$H, T = this.$m, z = this.$M, R = h.weekdays, Q = h.months, ee = h.meridiem, Z = function(L, J, ne, ae) {
            return L && (L[J] || L(m, y)) || ne[J].slice(0, ae);
          }, re = function(L) {
            return k.s(E % 12 || 12, L, "0");
          }, K = ee || function(L, J, ne) {
            var ae = L < 12 ? "AM" : "PM";
            return ne ? ae.toLowerCase() : ae;
          };
          return y.replace(A, (function(L, J) {
            return J || (function(ne) {
              switch (ne) {
                case "YY":
                  return String(m.$y).slice(-2);
                case "YYYY":
                  return k.s(m.$y, 4, "0");
                case "M":
                  return z + 1;
                case "MM":
                  return k.s(z + 1, 2, "0");
                case "MMM":
                  return Z(h.monthsShort, z, Q, 3);
                case "MMMM":
                  return Z(Q, z);
                case "D":
                  return m.$D;
                case "DD":
                  return k.s(m.$D, 2, "0");
                case "d":
                  return String(m.$W);
                case "dd":
                  return Z(h.weekdaysMin, m.$W, R, 2);
                case "ddd":
                  return Z(h.weekdaysShort, m.$W, R, 3);
                case "dddd":
                  return R[m.$W];
                case "H":
                  return String(E);
                case "HH":
                  return k.s(E, 2, "0");
                case "h":
                  return re(1);
                case "hh":
                  return re(2);
                case "a":
                  return K(E, T, !0);
                case "A":
                  return K(E, T, !1);
                case "m":
                  return String(T);
                case "mm":
                  return k.s(T, 2, "0");
                case "s":
                  return String(m.$s);
                case "ss":
                  return k.s(m.$s, 2, "0");
                case "SSS":
                  return k.s(m.$ms, 3, "0");
                case "Z":
                  return $;
              }
              return null;
            })(L) || $.replace(":", "");
          }));
        }, d.utcOffset = function() {
          return 15 * -Math.round(this.$d.getTimezoneOffset() / 15);
        }, d.diff = function(f, m, h) {
          var y, $ = this, E = k.p(m), T = H(f), z = (T.utcOffset() - this.utcOffset()) * n, R = this - T, Q = function() {
            return k.m($, T);
          };
          switch (E) {
            case p:
              y = Q() / 12;
              break;
            case u:
              y = Q();
              break;
            case v:
              y = Q() / 3;
              break;
            case l:
              y = (R - z) / 6048e5;
              break;
            case c:
              y = (R - z) / 864e5;
              break;
            case _:
              y = R / o;
              break;
            case a:
              y = R / n;
              break;
            case s:
              y = R / r;
              break;
            default:
              y = R;
          }
          return h ? y : k.a(y);
        }, d.daysInMonth = function() {
          return this.endOf(u).$D;
        }, d.$locale = function() {
          return O[this.$L];
        }, d.locale = function(f, m) {
          if (!f) return this.$L;
          var h = this.clone(), y = F(f, m, !0);
          return y && (h.$L = y), h;
        }, d.clone = function() {
          return k.w(this.$d, this);
        }, d.toDate = function() {
          return new Date(this.valueOf());
        }, d.toJSON = function() {
          return this.isValid() ? this.toISOString() : null;
        }, d.toISOString = function() {
          return this.$d.toISOString();
        }, d.toString = function() {
          return this.$d.toUTCString();
        }, g;
      })(), se = q.prototype;
      return H.prototype = se, [["$ms", i], ["$s", s], ["$m", a], ["$H", _], ["$W", c], ["$M", u], ["$y", p], ["$D", M]].forEach((function(g) {
        se[g[1]] = function(d) {
          return this.$g(d, g[0], g[1]);
        };
      })), H.extend = function(g, d) {
        return g.$i || (g(d, q, H), g.$i = !0), H;
      }, H.locale = F, H.isDayjs = B, H.unix = function(g) {
        return H(1e3 * g);
      }, H.en = O[D], H.Ls = O, H.p = {}, H;
    }));
  })(fe)), fe.exports;
}
var Mr = Dr();
const Et = /* @__PURE__ */ Sr(Mr);
var Or = 0;
function I(e, t, r, n, o, i) {
  t || (t = {});
  var s, a, _ = t;
  if ("ref" in _) for (a in _ = {}, t) a == "ref" ? s = t[a] : _[a] = t[a];
  var c = { type: e, props: _, key: r, ref: s, __k: null, __: null, __b: 0, __e: null, __c: null, constructor: void 0, __v: --Or, __i: -1, __u: 0, __source: o, __self: i };
  if (typeof e == "function" && (s = e.defaultProps)) for (a in s) _[a] === void 0 && (_[a] = s[a]);
  return w.vnode && w.vnode(c), c;
}
const Cr = {
  width: "50px",
  height: "50px",
  borderRadius: "30%",
  marginRight: "10px"
}, Ir = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAABg2lDQ1BJQ0MgcHJvZmlsZQAAKJF9kT1Iw0AcxV9TpVIrDnaQ4pChOtlFizjWKhShQqgVWnUwufQLmrQkKS6OgmvBwY/FqoOLs64OroIg+AHiLjgpukiJ/0sKLWI8OO7Hu3uPu3eA0KoyzexLAJpuGZlUUszlV8XAK4IIYBARxGVm1uckKQ3P8XUPH1/vYjzL+9yfY0gtmAzwicQJVjcs4g3imU2rznmfOMzKskp8Tjxp0AWJH7muuPzGueSwwDPDRjYzTxwmFks9rPQwKxsacZw4qmo65Qs5l1XOW5y1aoN17slfGCroK8tcpzmGFBaxBAkiFDRQQRUWYrTqpJjI0H7Swx9x/BK5FHJVwMixgBo0yI4f/A9+d2sWp6fcpFAS6H+x7Y9xILALtJu2/X1s2+0TwP8MXOldf60FzH6S3uxq0SNgeBu4uO5qyh5wuQOMPtVlQ3YkP02hWATez+ib8sDILRBcc3vr7OP0AchSV+kb4OAQmChR9rrHuwd6e/v3TKe/H6jOcrx3FVZ9AAAABmJLR0QA2gAcABw7O9rcAAAACXBIWXMAAC4jAAAuIwF4pT92AAAAB3RJTUUH6QoHCxweOtVPLQAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAAL2SURBVGje7Zk7aBRRFEDP7OxsNomfiAgGNRaKRfwQhFgkRhAh2ImQQu2SVGojItqIghIRLLQIEdRGTGGn0cakUCQkRQRB/AS0EY0Q4yfRZLMzuzPvWqzV7HPNfmY3E3Jhmzu8nXve/bx73xgiIiwBibBEZMmARIP4U5kFNQUyD2ID85ktM2qAGoish8iaRQgis+C+AW8M1DOQgf+vMQ6B2QHWAYjUF2+DUXCyq4zx6YegLhZnhNkLVZ1/PVZOEElCsgvkfulCwzgM8b5M2JUt2Y1qiGwvcV49APsEqOkyh5Y7Dk6jT7kSIqfBbAZzKxh1YMSBOJAGSYD6Au4weFeAKU2YXYb4+UJ2olBRIolukTlEEsdEnCERNbPw5d6ESKIrs97/S4/nb45RzMnuvgZciO4CzAI2cQaSR0AGfV7pg/jxclWtEkl6GFL7fMpWqH2e3+ZUHER+wXxdtr76Z36HZsVbFGM1sFsDmAhhr2Ws08Vc2EAUyKgGbkXIQNQkMKsBqQ0ZiDumMepU/n1XRUHUD0if05zuB0M0WIkNzgXgvS+k2sBqDQmI2GBfBdWX/czqyT/RA5sQc0LMgX0J1DWNMbfAaltEo+4/c+I72GdA7mryoiczXC2qmV0n3kdwukGeaiBuQPxkcdaUBcQdB6cDeKcxoB+qjhafrYGDeB/AaQcmsoew2ABY+0Nwr6W+gd2pgdgGVSOlgwgWRMDpBUZ8+maIP4HozhI3nkHNI+5bcHb4lI0QfwTmltK/LzCPuEPZutjtYCCCAxHw+n0vOgtWS3D5GAiImgZe+spjR7DVMRAQ3Zhqbg4hCI6mqqwKI4inAYkFCxLIyW6sBeuxXxnwBcbyN8RlkGWQyrTxahK8z4ALkY1gbgqbRzxw7kCyHlJ7INUCdgPY10FSIapa6RcZAJ1YgxBrD4lH1KsczhoNUWjJ7xwPp0IEYuT6OFMfIhCzKUeJ3BsikGgTRO9pAG8WfotY0V5LfQXvU+YcMRsgsmG5aVyQ/AHLzKTwE9NqZwAAAABJRU5ErkJggg==";
function Er(e) {
  return e.htmlUrl ? e.htmlUrl : e.id;
}
function Hr({
  actorInfo: e,
  style: t = Cr
}) {
  const r = e.avatarUrl || Ir, n = Er(e);
  return /* @__PURE__ */ I("a", { href: n, children: /* @__PURE__ */ I(
    "img",
    {
      style: {
        width: "50px",
        height: "50px",
        borderRadius: "30%",
        marginRight: "10px",
        ...t
      },
      src: r
    }
  ) });
}
const ot = {
  paddingTop: "5px",
  fontWeight: "bold"
}, Pr = {
  paddingTop: "5px",
  fontFamily: "monospace"
}, ve = { textDecoration: "none" };
function Tr(e) {
  return e.replace("acct:", "@");
}
function Ur({ actorInfo: e }) {
  const t = e.name || "- unknown -";
  return e.htmlUrl ? /* @__PURE__ */ I("div", { style: ot, children: /* @__PURE__ */ I("a", { style: ve, href: e.htmlUrl, children: t }) }) : /* @__PURE__ */ I("div", { style: ot, children: t });
}
function jr({ actorInfo: e }) {
  return /* @__PURE__ */ I("div", { style: Pr, children: /* @__PURE__ */ I("a", { style: ve, href: e.id, children: Tr(e.identifier) }) });
}
function Nr({ actorInfo: e, style: t }) {
  return /* @__PURE__ */ I("header", { style: { ...t, display: "flex" }, children: [
    /* @__PURE__ */ I(Hr, { actorInfo: e }),
    /* @__PURE__ */ I("span", { children: [
      /* @__PURE__ */ I(Ur, { actorInfo: e }),
      /* @__PURE__ */ I(jr, { actorInfo: e })
    ] })
  ] });
}
function zr(e) {
  return e && e.__esModule && Object.prototype.hasOwnProperty.call(e, "default") ? e.default : e;
}
var Me = { exports: {} }, Br = Me.exports, it;
function Rr() {
  return it || (it = 1, (function(e, t) {
    (function(r, n) {
      e.exports = n();
    })(Br, (function() {
      return function(r, n, o) {
        r = r || {};
        var i = n.prototype, s = { future: "in %s", past: "%s ago", s: "a few seconds", m: "a minute", mm: "%d minutes", h: "an hour", hh: "%d hours", d: "a day", dd: "%d days", M: "a month", MM: "%d months", y: "a year", yy: "%d years" };
        function a(c, l, u, v) {
          return i.fromToBase(c, l, u, v);
        }
        o.en.relativeTime = s, i.fromToBase = function(c, l, u, v, p) {
          for (var M, b, S, A = u.$locale().relativeTime || s, x = r.thresholds || [{ l: "s", r: 44, d: "second" }, { l: "m", r: 89 }, { l: "mm", r: 44, d: "minute" }, { l: "h", r: 89 }, { l: "hh", r: 21, d: "hour" }, { l: "d", r: 35 }, { l: "dd", r: 25, d: "day" }, { l: "M", r: 45 }, { l: "MM", r: 10, d: "month" }, { l: "y", r: 17 }, { l: "yy", d: "year" }], P = x.length, C = 0; C < P; C += 1) {
            var D = x[C];
            D.d && (M = v ? o(c).diff(u, D.d, !0) : u.diff(c, D.d, !0));
            var O = (r.rounding || Math.round)(Math.abs(M));
            if (S = M > 0, O <= D.r || !D.r) {
              O <= 1 && C > 0 && (D = x[C - 1]);
              var j = A[D.l];
              p && (O = p("" + O)), b = typeof j == "string" ? j.replace("%d", O) : j(O, l, D.l, S);
              break;
            }
          }
          if (l) return b;
          var B = S ? A.future : A.past;
          return typeof B == "function" ? B(b) : B.replace("%s", b);
        }, i.to = function(c, l) {
          return a(c, l, this, !0);
        }, i.from = function(c, l) {
          return a(c, l, this);
        };
        var _ = function(c) {
          return c.$u ? o.utc() : o();
        };
        i.toNow = function(c) {
          return this.to(_(this), c);
        }, i.fromNow = function(c) {
          return this.from(_(this), c);
        };
      };
    }));
  })(Me)), Me.exports;
}
var Wr = Rr();
const qr = /* @__PURE__ */ zr(Wr);
Et.extend(qr);
function st(e) {
  return Et(e).fromNow();
}
function Lr({ info: e }) {
  return e.updated ? /* @__PURE__ */ I(W, { children: [
    "edited, ",
    st(e.updated)
  ] }) : e.published ? /* @__PURE__ */ I(W, { children: st(e.published) }) : /* @__PURE__ */ I(W, { children: "post" });
}
function Fr({ info: e }) {
  return e.htmlUrl ? /* @__PURE__ */ I(W, { children: [
    ",",
    /* @__PURE__ */ I("a", { style: ve, href: e.htmlUrl, children: "www" })
  ] }) : /* @__PURE__ */ I(W, {});
}
function Vr({ info: e }) {
  return /* @__PURE__ */ I("div", { children: [
    /* @__PURE__ */ I("a", { style: ve, href: e.id, children: /* @__PURE__ */ I(Lr, { info: e }) }),
    /* @__PURE__ */ I(Fr, { info: e })
  ] });
}
function at({ data: e }) {
  return /* @__PURE__ */ I(
    "div",
    {
      className: "post",
      style: { border: "2px black solid", margin: "20px", padding: "20px" },
      children: [
        /* @__PURE__ */ I("div", { style: { display: "flex" }, children: [
          /* @__PURE__ */ I(Nr, { actorInfo: e.actorInfo, style: { flexGrow: 1 } }),
          /* @__PURE__ */ I(Vr, { info: e.metaInfo })
        ] }),
        /* @__PURE__ */ I("div", { dangerouslySetInnerHTML: { __html: e.content } })
      ]
    }
  );
}
function Qr(e) {
  const t = {};
  for (const r of e)
    r.replyOf in t || (t[r.replyOf] = []), t[r.replyOf].push(r);
  return t;
}
function Ht({ children: e, ordered: t, style: r }) {
  return /* @__PURE__ */ V("div", { style: { ...r }, children: e.map((n) => /* @__PURE__ */ V(Yr, { data: n, ordered: t }, n.metaInfo.id)) });
}
function Yr({ data: e, ordered: t }) {
  const r = t?.[e.metaInfo.id];
  return r ? /* @__PURE__ */ V(W, { children: [
    /* @__PURE__ */ V(at, { data: e }),
    /* @__PURE__ */ V(
      Ht,
      {
        children: r,
        ordered: t,
        style: { marginLeft: "50px" }
      }
    )
  ] }) : /* @__PURE__ */ V(at, { data: e });
}
function Gr({ commentData: e }) {
  const t = Qr(e.comments);
  return /* @__PURE__ */ V("div", { style: { lineHeight: 1 }, children: /* @__PURE__ */ V(
    Ht,
    {
      children: t[e.rootUri],
      ordered: t
    }
  ) });
}
function Jr({ baseUrl: e, encodedUrl: t }) {
  const [r, n] = Le(null), [o, i] = Le("loading");
  return It.setConfig({
    baseUrl: e
  }), Rt(() => {
    (async () => {
      const a = await Ar({
        path: {
          path: t
        }
      }), _ = a.response.status;
      _ == 200 && a.data ? a.data.comments.length == 0 ? i("noData") : (n(a.data), i("success")) : _ == 404 && i("noData");
    })();
  }, [e, t]), o == "loading" ? /* @__PURE__ */ V(W, { children: "Loading Comments" }) : o === "noData" ? /* @__PURE__ */ V(W, { children: "No comments" }) : o !== "success" || r == null ? /* @__PURE__ */ V(W, { children: "Something went wrong" }) : /* @__PURE__ */ V(Gr, { commentData: r });
}
function Zr(e, t, r) {
  const n = document.getElementById(e);
  if (!n) {
    console.error(`Element with id ${e} not found`);
    return;
  }
  ir(n).render(/* @__PURE__ */ V(Jr, { baseUrl: t, encodedUrl: r }));
}
export {
  Zr as add
};
