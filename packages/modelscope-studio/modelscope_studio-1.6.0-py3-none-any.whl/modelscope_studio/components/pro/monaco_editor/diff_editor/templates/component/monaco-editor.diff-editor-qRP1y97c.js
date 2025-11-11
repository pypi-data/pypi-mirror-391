import { i as De, a as le, r as Fe, b as We, c as ze, Z as $, g as Ae, d as Ue } from "./Index-8WHbvM3t.js";
const O = window.ms_globals.React, de = window.ms_globals.React.memo, H = window.ms_globals.React.useState, M = window.ms_globals.React.useRef, X = window.ms_globals.React.useCallback, T = window.ms_globals.React.useEffect, Ne = window.ms_globals.React.forwardRef, Ce = window.ms_globals.React.useMemo, xe = window.ms_globals.monacoLoader, je = window.ms_globals.internalContext.useContextPropsContext, se = window.ms_globals.ReactDOM.createPortal, He = window.ms_globals.antd.Spin;
var Ge = /\s/;
function Be(e) {
  for (var t = e.length; t-- && Ge.test(e.charAt(t)); )
    ;
  return t;
}
var Ke = /^\s+/;
function Ze(e) {
  return e && e.slice(0, Be(e) + 1).replace(Ke, "");
}
var fe = NaN, qe = /^[-+]0x[0-9a-f]+$/i, Je = /^0b[01]+$/i, Xe = /^0o[0-7]+$/i, Ye = parseInt;
function pe(e) {
  if (typeof e == "number")
    return e;
  if (De(e))
    return fe;
  if (le(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = le(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = Ze(e);
  var n = Je.test(e);
  return n || Xe.test(e) ? Ye(e.slice(2), n ? 2 : 8) : qe.test(e) ? fe : +e;
}
var ne = function() {
  return Fe.Date.now();
}, Qe = "Expected a function", $e = Math.max, et = Math.min;
function tt(e, t, n) {
  var o, s, r, i, l, f, _ = 0, S = !1, c = !1, I = !0;
  if (typeof e != "function")
    throw new TypeError(Qe);
  t = pe(t) || 0, le(n) && (S = !!n.leading, c = "maxWait" in n, r = c ? $e(pe(n.maxWait) || 0, t) : r, I = "trailing" in n ? !!n.trailing : I);
  function E(u) {
    var g = o, V = s;
    return o = s = void 0, _ = u, i = e.apply(V, g), i;
  }
  function L(u) {
    return _ = u, l = setTimeout(C, t), S ? E(u) : i;
  }
  function P(u) {
    var g = u - f, V = u - _, x = t - g;
    return c ? et(x, r - V) : x;
  }
  function m(u) {
    var g = u - f, V = u - _;
    return f === void 0 || g >= t || g < 0 || c && V >= r;
  }
  function C() {
    var u = ne();
    if (m(u))
      return b(u);
    l = setTimeout(C, P(u));
  }
  function b(u) {
    return l = void 0, I && o ? E(u) : (o = s = void 0, i);
  }
  function R() {
    l !== void 0 && clearTimeout(l), _ = 0, o = f = s = l = void 0;
  }
  function d() {
    return l === void 0 ? i : b(ne());
  }
  function w() {
    var u = ne(), g = m(u);
    if (o = arguments, s = this, f = u, g) {
      if (l === void 0)
        return L(f);
      if (c)
        return clearTimeout(l), l = setTimeout(C, t), E(f);
    }
    return l === void 0 && (l = setTimeout(C, t)), i;
  }
  return w.cancel = R, w.flush = d, w;
}
var rt = "[object Number]";
function ge(e) {
  return typeof e == "number" || We(e) && ze(e) == rt;
}
var Se = {
  exports: {}
}, re = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var nt = O, ot = Symbol.for("react.element"), it = Symbol.for("react.fragment"), st = Object.prototype.hasOwnProperty, lt = nt.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, at = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ke(e, t, n) {
  var o, s = {}, r = null, i = null;
  n !== void 0 && (r = "" + n), t.key !== void 0 && (r = "" + t.key), t.ref !== void 0 && (i = t.ref);
  for (o in t) st.call(t, o) && !at.hasOwnProperty(o) && (s[o] = t[o]);
  if (e && e.defaultProps) for (o in t = e.defaultProps, t) s[o] === void 0 && (s[o] = t[o]);
  return {
    $$typeof: ot,
    type: e,
    key: r,
    ref: i,
    props: s,
    _owner: lt.current
  };
}
re.Fragment = it;
re.jsx = ke;
re.jsxs = ke;
Se.exports = re;
var U = Se.exports, ut = {
  wrapper: {
    display: "flex",
    position: "relative",
    textAlign: "initial"
  },
  fullWidth: {
    width: "100%"
  },
  hide: {
    display: "none"
  }
}, oe = ut, ct = {
  container: {
    display: "flex",
    height: "100%",
    width: "100%",
    justifyContent: "center",
    alignItems: "center"
  }
}, dt = ct;
function ft({
  children: e
}) {
  return O.createElement("div", {
    style: dt.container
  }, e);
}
var pt = ft, gt = pt;
function mt({
  width: e,
  height: t,
  isEditorReady: n,
  loading: o,
  _ref: s,
  className: r,
  wrapperProps: i
}) {
  return O.createElement("section", {
    style: {
      ...oe.wrapper,
      width: e,
      height: t
    },
    ...i
  }, !n && O.createElement(gt, null, o), O.createElement("div", {
    ref: s,
    style: {
      ...oe.fullWidth,
      ...!n && oe.hide
    },
    className: r
  }));
}
var ht = mt, Ie = de(ht);
function _t(e) {
  T(e, []);
}
var Re = _t;
function wt(e, t, n = !0) {
  let o = M(!0);
  T(o.current || !n ? () => {
    o.current = !1;
  } : e, t);
}
var j = wt;
function J() {
}
function K(e, t, n, o) {
  return vt(e, o) || bt(e, t, n, o);
}
function vt(e, t) {
  return e.editor.getModel(Le(e, t));
}
function bt(e, t, n, o) {
  return e.editor.createModel(t, n, o ? Le(e, o) : void 0);
}
function Le(e, t) {
  return e.Uri.parse(t);
}
function yt({
  original: e,
  modified: t,
  language: n,
  originalLanguage: o,
  modifiedLanguage: s,
  originalModelPath: r,
  modifiedModelPath: i,
  keepCurrentOriginalModel: l = !1,
  keepCurrentModifiedModel: f = !1,
  theme: _ = "light",
  loading: S = "Loading...",
  options: c = {},
  height: I = "100%",
  width: E = "100%",
  className: L,
  wrapperProps: P = {},
  beforeMount: m = J,
  onMount: C = J
}) {
  let [b, R] = H(!1), [d, w] = H(!0), u = M(null), g = M(null), V = M(null), x = M(C), h = M(m), A = M(!1);
  Re(() => {
    let a = xe.init();
    return a.then((y) => (g.current = y) && w(!1)).catch((y) => (y == null ? void 0 : y.type) !== "cancelation" && console.error("Monaco initialization: error:", y)), () => u.current ? D() : a.cancel();
  }), j(() => {
    if (u.current && g.current) {
      let a = u.current.getOriginalEditor(), y = K(g.current, e || "", o || n || "text", r || "");
      y !== a.getModel() && a.setModel(y);
    }
  }, [r], b), j(() => {
    if (u.current && g.current) {
      let a = u.current.getModifiedEditor(), y = K(g.current, t || "", s || n || "text", i || "");
      y !== a.getModel() && a.setModel(y);
    }
  }, [i], b), j(() => {
    let a = u.current.getModifiedEditor();
    a.getOption(g.current.editor.EditorOption.readOnly) ? a.setValue(t || "") : t !== a.getValue() && (a.executeEdits("", [{
      range: a.getModel().getFullModelRange(),
      text: t || "",
      forceMoveMarkers: !0
    }]), a.pushUndoStop());
  }, [t], b), j(() => {
    var a, y;
    (y = (a = u.current) == null ? void 0 : a.getModel()) == null || y.original.setValue(e || "");
  }, [e], b), j(() => {
    let {
      original: a,
      modified: y
    } = u.current.getModel();
    g.current.editor.setModelLanguage(a, o || n || "text"), g.current.editor.setModelLanguage(y, s || n || "text");
  }, [n, o, s], b), j(() => {
    var a;
    (a = g.current) == null || a.editor.setTheme(_);
  }, [_], b), j(() => {
    var a;
    (a = u.current) == null || a.updateOptions(c);
  }, [c], b);
  let G = X(() => {
    var W;
    if (!g.current) return;
    h.current(g.current);
    let a = K(g.current, e || "", o || n || "text", r || ""), y = K(g.current, t || "", s || n || "text", i || "");
    (W = u.current) == null || W.setModel({
      original: a,
      modified: y
    });
  }, [n, t, s, e, o, r, i]), k = X(() => {
    var a;
    !A.current && V.current && (u.current = g.current.editor.createDiffEditor(V.current, {
      automaticLayout: !0,
      ...c
    }), G(), (a = g.current) == null || a.editor.setTheme(_), R(!0), A.current = !0);
  }, [c, _, G]);
  T(() => {
    b && x.current(u.current, g.current);
  }, [b]), T(() => {
    !d && !b && k();
  }, [d, b, k]);
  function D() {
    var y, W, z, F;
    let a = (y = u.current) == null ? void 0 : y.getModel();
    l || ((W = a == null ? void 0 : a.original) == null || W.dispose()), f || ((z = a == null ? void 0 : a.modified) == null || z.dispose()), (F = u.current) == null || F.dispose();
  }
  return O.createElement(Ie, {
    width: E,
    height: I,
    isEditorReady: b,
    loading: S,
    _ref: V,
    className: L,
    wrapperProps: P
  });
}
var Et = yt, Mt = de(Et);
function Ct(e) {
  let t = M();
  return T(() => {
    t.current = e;
  }, [e]), t.current;
}
var xt = Ct, Q = /* @__PURE__ */ new Map();
function St({
  defaultValue: e,
  defaultLanguage: t,
  defaultPath: n,
  value: o,
  language: s,
  path: r,
  theme: i = "light",
  line: l,
  loading: f = "Loading...",
  options: _ = {},
  overrideServices: S = {},
  saveViewState: c = !0,
  keepCurrentModel: I = !1,
  width: E = "100%",
  height: L = "100%",
  className: P,
  wrapperProps: m = {},
  beforeMount: C = J,
  onMount: b = J,
  onChange: R,
  onValidate: d = J
}) {
  let [w, u] = H(!1), [g, V] = H(!0), x = M(null), h = M(null), A = M(null), G = M(b), k = M(C), D = M(), a = M(o), y = xt(r), W = M(!1), z = M(!1);
  Re(() => {
    let p = xe.init();
    return p.then((v) => (x.current = v) && V(!1)).catch((v) => (v == null ? void 0 : v.type) !== "cancelation" && console.error("Monaco initialization: error:", v)), () => h.current ? Y() : p.cancel();
  }), j(() => {
    var v, N, q, B;
    let p = K(x.current, e || o || "", t || s || "", r || n || "");
    p !== ((v = h.current) == null ? void 0 : v.getModel()) && (c && Q.set(y, (N = h.current) == null ? void 0 : N.saveViewState()), (q = h.current) == null || q.setModel(p), c && ((B = h.current) == null || B.restoreViewState(Q.get(r))));
  }, [r], w), j(() => {
    var p;
    (p = h.current) == null || p.updateOptions(_);
  }, [_], w), j(() => {
    !h.current || o === void 0 || (h.current.getOption(x.current.editor.EditorOption.readOnly) ? h.current.setValue(o) : o !== h.current.getValue() && (z.current = !0, h.current.executeEdits("", [{
      range: h.current.getModel().getFullModelRange(),
      text: o,
      forceMoveMarkers: !0
    }]), h.current.pushUndoStop(), z.current = !1));
  }, [o], w), j(() => {
    var v, N;
    let p = (v = h.current) == null ? void 0 : v.getModel();
    p && s && ((N = x.current) == null || N.editor.setModelLanguage(p, s));
  }, [s], w), j(() => {
    var p;
    l !== void 0 && ((p = h.current) == null || p.revealLine(l));
  }, [l], w), j(() => {
    var p;
    (p = x.current) == null || p.editor.setTheme(i);
  }, [i], w);
  let F = X(() => {
    var p;
    if (!(!A.current || !x.current) && !W.current) {
      k.current(x.current);
      let v = r || n, N = K(x.current, o || e || "", t || s || "", v || "");
      h.current = (p = x.current) == null ? void 0 : p.editor.create(A.current, {
        model: N,
        automaticLayout: !0,
        ..._
      }, S), c && h.current.restoreViewState(Q.get(v)), x.current.editor.setTheme(i), l !== void 0 && h.current.revealLine(l), u(!0), W.current = !0;
    }
  }, [e, t, n, o, s, r, _, S, c, i, l]);
  T(() => {
    w && G.current(h.current, x.current);
  }, [w]), T(() => {
    !g && !w && F();
  }, [g, w, F]), a.current = o, T(() => {
    var p, v;
    w && R && ((p = D.current) == null || p.dispose(), D.current = (v = h.current) == null ? void 0 : v.onDidChangeModelContent((N) => {
      z.current || R(h.current.getValue(), N);
    }));
  }, [w, R]), T(() => {
    if (w) {
      let p = x.current.editor.onDidChangeMarkers((v) => {
        var q;
        let N = (q = h.current.getModel()) == null ? void 0 : q.uri;
        if (N && v.find((B) => B.path === N.path)) {
          let B = x.current.editor.getModelMarkers({
            resource: N
          });
          d == null || d(B);
        }
      });
      return () => {
        p == null || p.dispose();
      };
    }
    return () => {
    };
  }, [w, d]);
  function Y() {
    var p, v;
    (p = D.current) == null || p.dispose(), I ? c && Q.set(r, h.current.saveViewState()) : (v = h.current.getModel()) == null || v.dispose(), h.current.dispose();
  }
  return O.createElement(Ie, {
    width: E,
    height: L,
    isEditorReady: w,
    loading: f,
    _ref: A,
    className: P,
    wrapperProps: m
  });
}
var kt = St;
de(kt);
const It = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Rt(e) {
  return e ? Object.keys(e).reduce((t, n) => {
    const o = e[n];
    return t[n] = Lt(n, o), t;
  }, {}) : {};
}
function Lt(e, t) {
  return typeof t == "number" && !It.includes(e) ? t + "px" : t;
}
function ae(e) {
  const t = [], n = e.cloneNode(!1);
  if (e._reactElement) {
    const s = O.Children.toArray(e._reactElement.props.children).map((r) => {
      if (O.isValidElement(r) && r.props.__slot__) {
        const {
          portals: i,
          clonedElement: l
        } = ae(r.props.el);
        return O.cloneElement(r, {
          ...r.props,
          el: l,
          children: [...O.Children.toArray(r.props.children), ...i]
        });
      }
      return null;
    });
    return s.originalChildren = e._reactElement.props.children, t.push(se(O.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: s
    }), n)), {
      clonedElement: n,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((s) => {
    e.getEventListeners(s).forEach(({
      listener: i,
      type: l,
      useCapture: f
    }) => {
      n.addEventListener(l, i, f);
    });
  });
  const o = Array.from(e.childNodes);
  for (let s = 0; s < o.length; s++) {
    const r = o[s];
    if (r.nodeType === 1) {
      const {
        clonedElement: i,
        portals: l
      } = ae(r);
      t.push(...l), n.appendChild(i);
    } else r.nodeType === 3 && n.appendChild(r.cloneNode());
  }
  return {
    clonedElement: n,
    portals: t
  };
}
function Ot(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const Tt = Ne(({
  slot: e,
  clone: t,
  className: n,
  style: o,
  observeAttributes: s
}, r) => {
  const i = M(), [l, f] = H([]), {
    forceClone: _
  } = je(), S = _ ? !0 : t;
  return T(() => {
    var P;
    if (!i.current || !e)
      return;
    let c = e;
    function I() {
      let m = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (m = c.children[0], m.tagName.toLowerCase() === "react-portal-target" && m.children[0] && (m = m.children[0])), Ot(r, m), n && m.classList.add(...n.split(" ")), o) {
        const C = Rt(o);
        Object.keys(C).forEach((b) => {
          m.style[b] = C[b];
        });
      }
    }
    let E = null, L = null;
    if (S && window.MutationObserver) {
      let m = function() {
        var d, w, u;
        (d = i.current) != null && d.contains(c) && ((w = i.current) == null || w.removeChild(c));
        const {
          portals: b,
          clonedElement: R
        } = ae(e);
        c = R, f(b), c.style.display = "contents", L && clearTimeout(L), L = setTimeout(() => {
          I();
        }, 50), (u = i.current) == null || u.appendChild(c);
      };
      m();
      const C = tt(() => {
        m(), E == null || E.disconnect(), E == null || E.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: s
        });
      }, 50);
      E = new window.MutationObserver(C), E.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", I(), (P = i.current) == null || P.appendChild(c);
    return () => {
      var m, C;
      c.style.display = "", (m = i.current) != null && m.contains(c) && ((C = i.current) == null || C.removeChild(c)), E == null || E.disconnect();
    };
  }, [e, S, n, o, r, s, _]), O.createElement("react-child", {
    ref: i,
    style: {
      display: "contents"
    }
  }, ...l);
}), {
  SvelteComponent: Pt,
  assign: me,
  binding_callbacks: he,
  check_outros: Vt,
  children: Oe,
  claim_element: Te,
  claim_space: Nt,
  component_subscribe: _e,
  compute_slots: jt,
  create_slot: Dt,
  detach: Z,
  element: Pe,
  empty: we,
  exclude_internal_props: ve,
  get_all_dirty_from_scope: Ft,
  get_slot_changes: Wt,
  group_outros: zt,
  init: At,
  insert_hydration: ee,
  safe_not_equal: Ut,
  set_custom_element_data: Ve,
  space: Ht,
  transition_in: te,
  transition_out: ue,
  update_slot_base: Gt
} = window.__gradio__svelte__internal, {
  beforeUpdate: Bt,
  getContext: Kt,
  onDestroy: Zt,
  setContext: qt
} = window.__gradio__svelte__internal;
function be(e) {
  let t, n;
  const o = (
    /*#slots*/
    e[7].default
  ), s = Dt(
    o,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = Pe("svelte-slot"), s && s.c(), this.h();
    },
    l(r) {
      t = Te(r, "SVELTE-SLOT", {
        class: !0
      });
      var i = Oe(t);
      s && s.l(i), i.forEach(Z), this.h();
    },
    h() {
      Ve(t, "class", "svelte-1rt0kpf");
    },
    m(r, i) {
      ee(r, t, i), s && s.m(t, null), e[9](t), n = !0;
    },
    p(r, i) {
      s && s.p && (!n || i & /*$$scope*/
      64) && Gt(
        s,
        o,
        r,
        /*$$scope*/
        r[6],
        n ? Wt(
          o,
          /*$$scope*/
          r[6],
          i,
          null
        ) : Ft(
          /*$$scope*/
          r[6]
        ),
        null
      );
    },
    i(r) {
      n || (te(s, r), n = !0);
    },
    o(r) {
      ue(s, r), n = !1;
    },
    d(r) {
      r && Z(t), s && s.d(r), e[9](null);
    }
  };
}
function Jt(e) {
  let t, n, o, s, r = (
    /*$$slots*/
    e[4].default && be(e)
  );
  return {
    c() {
      t = Pe("react-portal-target"), n = Ht(), r && r.c(), o = we(), this.h();
    },
    l(i) {
      t = Te(i, "REACT-PORTAL-TARGET", {
        class: !0
      }), Oe(t).forEach(Z), n = Nt(i), r && r.l(i), o = we(), this.h();
    },
    h() {
      Ve(t, "class", "svelte-1rt0kpf");
    },
    m(i, l) {
      ee(i, t, l), e[8](t), ee(i, n, l), r && r.m(i, l), ee(i, o, l), s = !0;
    },
    p(i, [l]) {
      /*$$slots*/
      i[4].default ? r ? (r.p(i, l), l & /*$$slots*/
      16 && te(r, 1)) : (r = be(i), r.c(), te(r, 1), r.m(o.parentNode, o)) : r && (zt(), ue(r, 1, 1, () => {
        r = null;
      }), Vt());
    },
    i(i) {
      s || (te(r), s = !0);
    },
    o(i) {
      ue(r), s = !1;
    },
    d(i) {
      i && (Z(t), Z(n), Z(o)), e[8](null), r && r.d(i);
    }
  };
}
function ye(e) {
  const {
    svelteInit: t,
    ...n
  } = e;
  return n;
}
function Xt(e, t, n) {
  let o, s, {
    $$slots: r = {},
    $$scope: i
  } = t;
  const l = jt(r);
  let {
    svelteInit: f
  } = t;
  const _ = $(ye(t)), S = $();
  _e(e, S, (d) => n(0, o = d));
  const c = $();
  _e(e, c, (d) => n(1, s = d));
  const I = [], E = Kt("$$ms-gr-react-wrapper"), {
    slotKey: L,
    slotIndex: P,
    subSlotIndex: m
  } = Ae() || {}, C = f({
    parent: E,
    props: _,
    target: S,
    slot: c,
    slotKey: L,
    slotIndex: P,
    subSlotIndex: m,
    onDestroy(d) {
      I.push(d);
    }
  });
  qt("$$ms-gr-react-wrapper", C), Bt(() => {
    _.set(ye(t));
  }), Zt(() => {
    I.forEach((d) => d());
  });
  function b(d) {
    he[d ? "unshift" : "push"](() => {
      o = d, S.set(o);
    });
  }
  function R(d) {
    he[d ? "unshift" : "push"](() => {
      s = d, c.set(s);
    });
  }
  return e.$$set = (d) => {
    n(17, t = me(me({}, t), ve(d))), "svelteInit" in d && n(5, f = d.svelteInit), "$$scope" in d && n(6, i = d.$$scope);
  }, t = ve(t), [o, s, S, c, l, f, i, r, b, R];
}
class Yt extends Pt {
  constructor(t) {
    super(), At(this, t, Xt, Jt, Ut, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: nr
} = window.__gradio__svelte__internal, Ee = window.ms_globals.rerender, ie = window.ms_globals.tree;
function Qt(e, t = {}) {
  function n(o) {
    const s = $(), r = new Yt({
      ...o,
      props: {
        svelteInit(i) {
          window.ms_globals.autokey += 1;
          const l = {
            key: window.ms_globals.autokey,
            svelteInstance: s,
            reactComponent: e,
            props: i.props,
            slot: i.slot,
            target: i.target,
            slotIndex: i.slotIndex,
            subSlotIndex: i.subSlotIndex,
            ignore: t.ignore,
            slotKey: i.slotKey,
            nodes: []
          }, f = i.parent ?? ie;
          return f.nodes = [...f.nodes, l], Ee({
            createPortal: se,
            node: ie
          }), i.onDestroy(() => {
            f.nodes = f.nodes.filter((_) => _.svelteInstance !== s), Ee({
              createPortal: se,
              node: ie
            });
          }), l;
        },
        ...o.props
      }
    });
    return s.set(r), r;
  }
  return new Promise((o) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((s) => {
      window.ms_globals.initialize = () => {
        s();
      };
    })), window.ms_globals.initializePromise.then(() => {
      o(n);
    });
  });
}
function $t(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function er(e, t = !1) {
  try {
    if (Ue(e))
      return e;
    if (t && !$t(e))
      return;
    if (typeof e == "string") {
      let n = e.trim();
      return n.startsWith(";") && (n = n.slice(1)), n.endsWith(";") && (n = n.slice(0, -1)), new Function(`return (...args) => (${n})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function Me(e, t) {
  return Ce(() => er(e, t), [e, t]);
}
function ce(e) {
  const t = M(e);
  return t.current = e, X((...n) => {
    var o;
    return (o = t.current) == null ? void 0 : o.call(t, ...n);
  }, []);
}
function tr(e) {
  const {
    value: t,
    onValueChange: n
  } = e, [o, s] = H(!1), [r, i] = H(t), l = M(null), f = ce(n), _ = X((S) => {
    l.current && clearTimeout(l.current), s(!0), l.current = setTimeout(() => {
      s(!1);
    }, 100), f(S);
  }, [f]);
  return T(() => {
    o || i(t);
  }, [o, t]), T(() => () => {
    l.current && (clearTimeout(l.current), l.current = null);
  }, []), [r, _];
}
const or = Qt(({
  height: e,
  className: t,
  style: n,
  themeMode: o,
  slots: s,
  beforeMount: r,
  afterMount: i,
  children: l,
  onMount: f,
  onChange: _,
  onValueChange: S,
  onValidate: c,
  value: I,
  modified: E,
  options: L,
  readOnly: P,
  line: m,
  ...C
}) => {
  const b = Me(r), R = Me(i), d = M([]), w = M(null), [u, g] = O.useState(!1), [V, x] = tr({
    onValueChange: S,
    value: I
  }), h = ce(_), A = ce(c), G = (k, D) => {
    w.current = k, ge(m) && k.revealLine(m), g(!0);
    const a = k.getModifiedEditor(), y = a.onDidChangeModelContent((z) => {
      const F = a.getValue();
      x(F), h(F, z);
    }), W = D.editor.onDidChangeMarkers((z) => {
      var Y;
      const F = (Y = a.getModel()) == null ? void 0 : Y.uri;
      if (F && z.find((v) => v.path === F.path)) {
        const v = D.editor.getModelMarkers({
          resource: F
        });
        A(v);
      }
    });
    d.current.push(y, W);
  };
  return T(() => () => {
    d.current.forEach((k) => {
      k.dispose();
    });
  }, []), T(() => {
    var k;
    u && ge(m) && ((k = w.current) == null || k.revealLine(m));
  }, [m, u]), /* @__PURE__ */ U.jsxs(U.Fragment, {
    children: [/* @__PURE__ */ U.jsx("div", {
      style: {
        display: "none"
      },
      children: l
    }), /* @__PURE__ */ U.jsx("div", {
      className: t,
      style: {
        ...n,
        height: e
      },
      children: /* @__PURE__ */ U.jsx(Mt, {
        ...C,
        options: Ce(() => ({
          readOnly: P,
          ...L || {}
        }), [L, P]),
        modified: V || E,
        beforeMount: b,
        onMount: (k, D) => {
          G(k, D), f == null || f(k, D), R == null || R(k, D);
        },
        loading: s.loading ? /* @__PURE__ */ U.jsx(Tt, {
          slot: s.loading
        }) : /* @__PURE__ */ U.jsx(He, {
          tip: C.loading,
          wrapperClassName: "ms-gr-pro-monaco-editor-spin",
          children: /* @__PURE__ */ U.jsx("div", {})
        }),
        theme: o === "dark" ? "vs-dark" : "light"
      })
    })]
  });
});
export {
  or as MonacoDiffEditor,
  or as default
};
