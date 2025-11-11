import { i as Ne, a as le, r as je, Z as Q, g as Fe, b as We } from "./Index-D2GiTQmQ.js";
const T = window.ms_globals.React, ae = window.ms_globals.React.memo, W = window.ms_globals.React.useState, C = window.ms_globals.React.useRef, q = window.ms_globals.React.useCallback, V = window.ms_globals.React.useEffect, Pe = window.ms_globals.React.forwardRef, be = window.ms_globals.React.useMemo, Ee = window.ms_globals.monacoLoader, Ve = window.ms_globals.internalContext.useContextPropsContext, ie = window.ms_globals.ReactDOM.createPortal, Ae = window.ms_globals.antd.Spin;
var De = /\s/;
function ze(e) {
  for (var t = e.length; t-- && De.test(e.charAt(t)); )
    ;
  return t;
}
var Ue = /^\s+/;
function He(e) {
  return e && e.slice(0, ze(e) + 1).replace(Ue, "");
}
var ce = NaN, Be = /^[-+]0x[0-9a-f]+$/i, Ge = /^0b[01]+$/i, Ke = /^0o[0-7]+$/i, Ze = parseInt;
function de(e) {
  if (typeof e == "number")
    return e;
  if (Ne(e))
    return ce;
  if (le(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = le(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = He(e);
  var n = Ge.test(e);
  return n || Ke.test(e) ? Ze(e.slice(2), n ? 2 : 8) : Be.test(e) ? ce : +e;
}
var re = function() {
  return je.Date.now();
}, qe = "Expected a function", Je = Math.max, Xe = Math.min;
function Ye(e, t, n) {
  var o, l, r, i, s, p, g = 0, x = !1, u = !1, k = !0;
  if (typeof e != "function")
    throw new TypeError(qe);
  t = de(t) || 0, le(n) && (x = !!n.leading, u = "maxWait" in n, r = u ? Je(de(n.maxWait) || 0, t) : r, k = "trailing" in n ? !!n.trailing : k);
  function v(c) {
    var m = o, N = l;
    return o = l = void 0, g = c, i = e.apply(N, m), i;
  }
  function O(c) {
    return g = c, s = setTimeout(M, t), x ? v(c) : i;
  }
  function P(c) {
    var m = c - p, N = c - g, S = t - m;
    return u ? Xe(S, r - N) : S;
  }
  function h(c) {
    var m = c - p, N = c - g;
    return p === void 0 || m >= t || m < 0 || u && N >= r;
  }
  function M() {
    var c = re();
    if (h(c))
      return w(c);
    s = setTimeout(M, P(c));
  }
  function w(c) {
    return s = void 0, k && o ? v(c) : (o = l = void 0, i);
  }
  function I() {
    s !== void 0 && clearTimeout(s), g = 0, o = p = l = s = void 0;
  }
  function d() {
    return s === void 0 ? i : w(re());
  }
  function y() {
    var c = re(), m = h(c);
    if (o = arguments, l = this, p = c, m) {
      if (s === void 0)
        return O(p);
      if (u)
        return clearTimeout(s), s = setTimeout(M, t), v(p);
    }
    return s === void 0 && (s = setTimeout(M, t)), i;
  }
  return y.cancel = I, y.flush = d, y;
}
var Me = {
  exports: {}
}, te = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Qe = T, $e = Symbol.for("react.element"), et = Symbol.for("react.fragment"), tt = Object.prototype.hasOwnProperty, rt = Qe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, nt = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Ce(e, t, n) {
  var o, l = {}, r = null, i = null;
  n !== void 0 && (r = "" + n), t.key !== void 0 && (r = "" + t.key), t.ref !== void 0 && (i = t.ref);
  for (o in t) tt.call(t, o) && !nt.hasOwnProperty(o) && (l[o] = t[o]);
  if (e && e.defaultProps) for (o in t = e.defaultProps, t) l[o] === void 0 && (l[o] = t[o]);
  return {
    $$typeof: $e,
    type: e,
    key: r,
    ref: i,
    props: l,
    _owner: rt.current
  };
}
te.Fragment = et;
te.jsx = Ce;
te.jsxs = Ce;
Me.exports = te;
var F = Me.exports, ot = {
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
}, ne = ot, it = {
  container: {
    display: "flex",
    height: "100%",
    width: "100%",
    justifyContent: "center",
    alignItems: "center"
  }
}, lt = it;
function st({
  children: e
}) {
  return T.createElement("div", {
    style: lt.container
  }, e);
}
var ut = st, at = ut;
function ct({
  width: e,
  height: t,
  isEditorReady: n,
  loading: o,
  _ref: l,
  className: r,
  wrapperProps: i
}) {
  return T.createElement("section", {
    style: {
      ...ne.wrapper,
      width: e,
      height: t
    },
    ...i
  }, !n && T.createElement(at, null, o), T.createElement("div", {
    ref: l,
    style: {
      ...ne.fullWidth,
      ...!n && ne.hide
    },
    className: r
  }));
}
var dt = ct, xe = ae(dt);
function ft(e) {
  V(e, []);
}
var Se = ft;
function pt(e, t, n = !0) {
  let o = C(!0);
  V(o.current || !n ? () => {
    o.current = !1;
  } : e, t);
}
var L = pt;
function Z() {
}
function U(e, t, n, o) {
  return mt(e, o) || gt(e, t, n, o);
}
function mt(e, t) {
  return e.editor.getModel(Ie(e, t));
}
function gt(e, t, n, o) {
  return e.editor.createModel(t, n, o ? Ie(e, o) : void 0);
}
function Ie(e, t) {
  return e.Uri.parse(t);
}
function ht({
  original: e,
  modified: t,
  language: n,
  originalLanguage: o,
  modifiedLanguage: l,
  originalModelPath: r,
  modifiedModelPath: i,
  keepCurrentOriginalModel: s = !1,
  keepCurrentModifiedModel: p = !1,
  theme: g = "light",
  loading: x = "Loading...",
  options: u = {},
  height: k = "100%",
  width: v = "100%",
  className: O,
  wrapperProps: P = {},
  beforeMount: h = Z,
  onMount: M = Z
}) {
  let [w, I] = W(!1), [d, y] = W(!0), c = C(null), m = C(null), N = C(null), S = C(M), _ = C(h), A = C(!1);
  Se(() => {
    let a = Ee.init();
    return a.then((b) => (m.current = b) && y(!1)).catch((b) => (b == null ? void 0 : b.type) !== "cancelation" && console.error("Monaco initialization: error:", b)), () => c.current ? B() : a.cancel();
  }), L(() => {
    if (c.current && m.current) {
      let a = c.current.getOriginalEditor(), b = U(m.current, e || "", o || n || "text", r || "");
      b !== a.getModel() && a.setModel(b);
    }
  }, [r], w), L(() => {
    if (c.current && m.current) {
      let a = c.current.getModifiedEditor(), b = U(m.current, t || "", l || n || "text", i || "");
      b !== a.getModel() && a.setModel(b);
    }
  }, [i], w), L(() => {
    let a = c.current.getModifiedEditor();
    a.getOption(m.current.editor.EditorOption.readOnly) ? a.setValue(t || "") : t !== a.getValue() && (a.executeEdits("", [{
      range: a.getModel().getFullModelRange(),
      text: t || "",
      forceMoveMarkers: !0
    }]), a.pushUndoStop());
  }, [t], w), L(() => {
    var a, b;
    (b = (a = c.current) == null ? void 0 : a.getModel()) == null || b.original.setValue(e || "");
  }, [e], w), L(() => {
    let {
      original: a,
      modified: b
    } = c.current.getModel();
    m.current.editor.setModelLanguage(a, o || n || "text"), m.current.editor.setModelLanguage(b, l || n || "text");
  }, [n, o, l], w), L(() => {
    var a;
    (a = m.current) == null || a.editor.setTheme(g);
  }, [g], w), L(() => {
    var a;
    (a = c.current) == null || a.updateOptions(u);
  }, [u], w);
  let J = q(() => {
    var j;
    if (!m.current) return;
    _.current(m.current);
    let a = U(m.current, e || "", o || n || "text", r || ""), b = U(m.current, t || "", l || n || "text", i || "");
    (j = c.current) == null || j.setModel({
      original: a,
      modified: b
    });
  }, [n, t, l, e, o, r, i]), X = q(() => {
    var a;
    !A.current && N.current && (c.current = m.current.editor.createDiffEditor(N.current, {
      automaticLayout: !0,
      ...u
    }), J(), (a = m.current) == null || a.editor.setTheme(g), I(!0), A.current = !0);
  }, [u, g, J]);
  V(() => {
    w && S.current(c.current, m.current);
  }, [w]), V(() => {
    !d && !w && X();
  }, [d, w, X]);
  function B() {
    var b, j, D, G;
    let a = (b = c.current) == null ? void 0 : b.getModel();
    s || ((j = a == null ? void 0 : a.original) == null || j.dispose()), p || ((D = a == null ? void 0 : a.modified) == null || D.dispose()), (G = c.current) == null || G.dispose();
  }
  return T.createElement(xe, {
    width: v,
    height: k,
    isEditorReady: w,
    loading: x,
    _ref: N,
    className: O,
    wrapperProps: P
  });
}
var _t = ht;
ae(_t);
function wt(e) {
  let t = C();
  return V(() => {
    t.current = e;
  }, [e]), t.current;
}
var vt = wt, Y = /* @__PURE__ */ new Map();
function yt({
  defaultValue: e,
  defaultLanguage: t,
  defaultPath: n,
  value: o,
  language: l,
  path: r,
  theme: i = "light",
  line: s,
  loading: p = "Loading...",
  options: g = {},
  overrideServices: x = {},
  saveViewState: u = !0,
  keepCurrentModel: k = !1,
  width: v = "100%",
  height: O = "100%",
  className: P,
  wrapperProps: h = {},
  beforeMount: M = Z,
  onMount: w = Z,
  onChange: I,
  onValidate: d = Z
}) {
  let [y, c] = W(!1), [m, N] = W(!0), S = C(null), _ = C(null), A = C(null), J = C(w), X = C(M), B = C(), a = C(o), b = vt(r), j = C(!1), D = C(!1);
  Se(() => {
    let f = Ee.init();
    return f.then((E) => (S.current = E) && N(!1)).catch((E) => (E == null ? void 0 : E.type) !== "cancelation" && console.error("Monaco initialization: error:", E)), () => _.current ? Te() : f.cancel();
  }), L(() => {
    var E, R, K, z;
    let f = U(S.current, e || o || "", t || l || "", r || n || "");
    f !== ((E = _.current) == null ? void 0 : E.getModel()) && (u && Y.set(b, (R = _.current) == null ? void 0 : R.saveViewState()), (K = _.current) == null || K.setModel(f), u && ((z = _.current) == null || z.restoreViewState(Y.get(r))));
  }, [r], y), L(() => {
    var f;
    (f = _.current) == null || f.updateOptions(g);
  }, [g], y), L(() => {
    !_.current || o === void 0 || (_.current.getOption(S.current.editor.EditorOption.readOnly) ? _.current.setValue(o) : o !== _.current.getValue() && (D.current = !0, _.current.executeEdits("", [{
      range: _.current.getModel().getFullModelRange(),
      text: o,
      forceMoveMarkers: !0
    }]), _.current.pushUndoStop(), D.current = !1));
  }, [o], y), L(() => {
    var E, R;
    let f = (E = _.current) == null ? void 0 : E.getModel();
    f && l && ((R = S.current) == null || R.editor.setModelLanguage(f, l));
  }, [l], y), L(() => {
    var f;
    s !== void 0 && ((f = _.current) == null || f.revealLine(s));
  }, [s], y), L(() => {
    var f;
    (f = S.current) == null || f.editor.setTheme(i);
  }, [i], y);
  let G = q(() => {
    var f;
    if (!(!A.current || !S.current) && !j.current) {
      X.current(S.current);
      let E = r || n, R = U(S.current, o || e || "", t || l || "", E || "");
      _.current = (f = S.current) == null ? void 0 : f.editor.create(A.current, {
        model: R,
        automaticLayout: !0,
        ...g
      }, x), u && _.current.restoreViewState(Y.get(E)), S.current.editor.setTheme(i), s !== void 0 && _.current.revealLine(s), c(!0), j.current = !0;
    }
  }, [e, t, n, o, l, r, g, x, u, i, s]);
  V(() => {
    y && J.current(_.current, S.current);
  }, [y]), V(() => {
    !m && !y && G();
  }, [m, y, G]), a.current = o, V(() => {
    var f, E;
    y && I && ((f = B.current) == null || f.dispose(), B.current = (E = _.current) == null ? void 0 : E.onDidChangeModelContent((R) => {
      D.current || I(_.current.getValue(), R);
    }));
  }, [y, I]), V(() => {
    if (y) {
      let f = S.current.editor.onDidChangeMarkers((E) => {
        var K;
        let R = (K = _.current.getModel()) == null ? void 0 : K.uri;
        if (R && E.find((z) => z.path === R.path)) {
          let z = S.current.editor.getModelMarkers({
            resource: R
          });
          d == null || d(z);
        }
      });
      return () => {
        f == null || f.dispose();
      };
    }
    return () => {
    };
  }, [y, d]);
  function Te() {
    var f, E;
    (f = B.current) == null || f.dispose(), k ? u && Y.set(r, _.current.saveViewState()) : (E = _.current.getModel()) == null || E.dispose(), _.current.dispose();
  }
  return T.createElement(xe, {
    width: v,
    height: O,
    isEditorReady: y,
    loading: p,
    _ref: A,
    className: P,
    wrapperProps: h
  });
}
var bt = yt, Et = ae(bt);
const Mt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Ct(e) {
  return e ? Object.keys(e).reduce((t, n) => {
    const o = e[n];
    return t[n] = xt(n, o), t;
  }, {}) : {};
}
function xt(e, t) {
  return typeof t == "number" && !Mt.includes(e) ? t + "px" : t;
}
function se(e) {
  const t = [], n = e.cloneNode(!1);
  if (e._reactElement) {
    const l = T.Children.toArray(e._reactElement.props.children).map((r) => {
      if (T.isValidElement(r) && r.props.__slot__) {
        const {
          portals: i,
          clonedElement: s
        } = se(r.props.el);
        return T.cloneElement(r, {
          ...r.props,
          el: s,
          children: [...T.Children.toArray(r.props.children), ...i]
        });
      }
      return null;
    });
    return l.originalChildren = e._reactElement.props.children, t.push(ie(T.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: l
    }), n)), {
      clonedElement: n,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((l) => {
    e.getEventListeners(l).forEach(({
      listener: i,
      type: s,
      useCapture: p
    }) => {
      n.addEventListener(s, i, p);
    });
  });
  const o = Array.from(e.childNodes);
  for (let l = 0; l < o.length; l++) {
    const r = o[l];
    if (r.nodeType === 1) {
      const {
        clonedElement: i,
        portals: s
      } = se(r);
      t.push(...s), n.appendChild(i);
    } else r.nodeType === 3 && n.appendChild(r.cloneNode());
  }
  return {
    clonedElement: n,
    portals: t
  };
}
function St(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const It = Pe(({
  slot: e,
  clone: t,
  className: n,
  style: o,
  observeAttributes: l
}, r) => {
  const i = C(), [s, p] = W([]), {
    forceClone: g
  } = Ve(), x = g ? !0 : t;
  return V(() => {
    var P;
    if (!i.current || !e)
      return;
    let u = e;
    function k() {
      let h = u;
      if (u.tagName.toLowerCase() === "svelte-slot" && u.children.length === 1 && u.children[0] && (h = u.children[0], h.tagName.toLowerCase() === "react-portal-target" && h.children[0] && (h = h.children[0])), St(r, h), n && h.classList.add(...n.split(" ")), o) {
        const M = Ct(o);
        Object.keys(M).forEach((w) => {
          h.style[w] = M[w];
        });
      }
    }
    let v = null, O = null;
    if (x && window.MutationObserver) {
      let h = function() {
        var d, y, c;
        (d = i.current) != null && d.contains(u) && ((y = i.current) == null || y.removeChild(u));
        const {
          portals: w,
          clonedElement: I
        } = se(e);
        u = I, p(w), u.style.display = "contents", O && clearTimeout(O), O = setTimeout(() => {
          k();
        }, 50), (c = i.current) == null || c.appendChild(u);
      };
      h();
      const M = Ye(() => {
        h(), v == null || v.disconnect(), v == null || v.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: l
        });
      }, 50);
      v = new window.MutationObserver(M), v.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      u.style.display = "contents", k(), (P = i.current) == null || P.appendChild(u);
    return () => {
      var h, M;
      u.style.display = "", (h = i.current) != null && h.contains(u) && ((M = i.current) == null || M.removeChild(u)), v == null || v.disconnect();
    };
  }, [e, x, n, o, r, l, g]), T.createElement("react-child", {
    ref: i,
    style: {
      display: "contents"
    }
  }, ...s);
}), {
  SvelteComponent: kt,
  assign: fe,
  binding_callbacks: pe,
  check_outros: Ot,
  children: ke,
  claim_element: Oe,
  claim_space: Rt,
  component_subscribe: me,
  compute_slots: Lt,
  create_slot: Tt,
  detach: H,
  element: Re,
  empty: ge,
  exclude_internal_props: he,
  get_all_dirty_from_scope: Pt,
  get_slot_changes: Vt,
  group_outros: Nt,
  init: jt,
  insert_hydration: $,
  safe_not_equal: Ft,
  set_custom_element_data: Le,
  space: Wt,
  transition_in: ee,
  transition_out: ue,
  update_slot_base: At
} = window.__gradio__svelte__internal, {
  beforeUpdate: Dt,
  getContext: zt,
  onDestroy: Ut,
  setContext: Ht
} = window.__gradio__svelte__internal;
function _e(e) {
  let t, n;
  const o = (
    /*#slots*/
    e[7].default
  ), l = Tt(
    o,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = Re("svelte-slot"), l && l.c(), this.h();
    },
    l(r) {
      t = Oe(r, "SVELTE-SLOT", {
        class: !0
      });
      var i = ke(t);
      l && l.l(i), i.forEach(H), this.h();
    },
    h() {
      Le(t, "class", "svelte-1rt0kpf");
    },
    m(r, i) {
      $(r, t, i), l && l.m(t, null), e[9](t), n = !0;
    },
    p(r, i) {
      l && l.p && (!n || i & /*$$scope*/
      64) && At(
        l,
        o,
        r,
        /*$$scope*/
        r[6],
        n ? Vt(
          o,
          /*$$scope*/
          r[6],
          i,
          null
        ) : Pt(
          /*$$scope*/
          r[6]
        ),
        null
      );
    },
    i(r) {
      n || (ee(l, r), n = !0);
    },
    o(r) {
      ue(l, r), n = !1;
    },
    d(r) {
      r && H(t), l && l.d(r), e[9](null);
    }
  };
}
function Bt(e) {
  let t, n, o, l, r = (
    /*$$slots*/
    e[4].default && _e(e)
  );
  return {
    c() {
      t = Re("react-portal-target"), n = Wt(), r && r.c(), o = ge(), this.h();
    },
    l(i) {
      t = Oe(i, "REACT-PORTAL-TARGET", {
        class: !0
      }), ke(t).forEach(H), n = Rt(i), r && r.l(i), o = ge(), this.h();
    },
    h() {
      Le(t, "class", "svelte-1rt0kpf");
    },
    m(i, s) {
      $(i, t, s), e[8](t), $(i, n, s), r && r.m(i, s), $(i, o, s), l = !0;
    },
    p(i, [s]) {
      /*$$slots*/
      i[4].default ? r ? (r.p(i, s), s & /*$$slots*/
      16 && ee(r, 1)) : (r = _e(i), r.c(), ee(r, 1), r.m(o.parentNode, o)) : r && (Nt(), ue(r, 1, 1, () => {
        r = null;
      }), Ot());
    },
    i(i) {
      l || (ee(r), l = !0);
    },
    o(i) {
      ue(r), l = !1;
    },
    d(i) {
      i && (H(t), H(n), H(o)), e[8](null), r && r.d(i);
    }
  };
}
function we(e) {
  const {
    svelteInit: t,
    ...n
  } = e;
  return n;
}
function Gt(e, t, n) {
  let o, l, {
    $$slots: r = {},
    $$scope: i
  } = t;
  const s = Lt(r);
  let {
    svelteInit: p
  } = t;
  const g = Q(we(t)), x = Q();
  me(e, x, (d) => n(0, o = d));
  const u = Q();
  me(e, u, (d) => n(1, l = d));
  const k = [], v = zt("$$ms-gr-react-wrapper"), {
    slotKey: O,
    slotIndex: P,
    subSlotIndex: h
  } = Fe() || {}, M = p({
    parent: v,
    props: g,
    target: x,
    slot: u,
    slotKey: O,
    slotIndex: P,
    subSlotIndex: h,
    onDestroy(d) {
      k.push(d);
    }
  });
  Ht("$$ms-gr-react-wrapper", M), Dt(() => {
    g.set(we(t));
  }), Ut(() => {
    k.forEach((d) => d());
  });
  function w(d) {
    pe[d ? "unshift" : "push"](() => {
      o = d, x.set(o);
    });
  }
  function I(d) {
    pe[d ? "unshift" : "push"](() => {
      l = d, u.set(l);
    });
  }
  return e.$$set = (d) => {
    n(17, t = fe(fe({}, t), he(d))), "svelteInit" in d && n(5, p = d.svelteInit), "$$scope" in d && n(6, i = d.$$scope);
  }, t = he(t), [o, l, x, u, s, p, i, r, w, I];
}
class Kt extends kt {
  constructor(t) {
    super(), jt(this, t, Gt, Bt, Ft, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: $t
} = window.__gradio__svelte__internal, ve = window.ms_globals.rerender, oe = window.ms_globals.tree;
function Zt(e, t = {}) {
  function n(o) {
    const l = Q(), r = new Kt({
      ...o,
      props: {
        svelteInit(i) {
          window.ms_globals.autokey += 1;
          const s = {
            key: window.ms_globals.autokey,
            svelteInstance: l,
            reactComponent: e,
            props: i.props,
            slot: i.slot,
            target: i.target,
            slotIndex: i.slotIndex,
            subSlotIndex: i.subSlotIndex,
            ignore: t.ignore,
            slotKey: i.slotKey,
            nodes: []
          }, p = i.parent ?? oe;
          return p.nodes = [...p.nodes, s], ve({
            createPortal: ie,
            node: oe
          }), i.onDestroy(() => {
            p.nodes = p.nodes.filter((g) => g.svelteInstance !== l), ve({
              createPortal: ie,
              node: oe
            });
          }), s;
        },
        ...o.props
      }
    });
    return l.set(r), r;
  }
  return new Promise((o) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((l) => {
      window.ms_globals.initialize = () => {
        l();
      };
    })), window.ms_globals.initializePromise.then(() => {
      o(n);
    });
  });
}
function qt(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function Jt(e, t = !1) {
  try {
    if (We(e))
      return e;
    if (t && !qt(e))
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
function ye(e, t) {
  return be(() => Jt(e, t), [e, t]);
}
function Xt(e) {
  const t = C(e);
  return t.current = e, q((...n) => {
    var o;
    return (o = t.current) == null ? void 0 : o.call(t, ...n);
  }, []);
}
function Yt(e) {
  const {
    value: t,
    onValueChange: n
  } = e, [o, l] = W(!1), [r, i] = W(t), s = C(null), p = Xt(n), g = q((x) => {
    s.current && clearTimeout(s.current), l(!0), s.current = setTimeout(() => {
      l(!1);
    }, 100), p(x);
  }, [p]);
  return V(() => {
    o || i(t);
  }, [o, t]), V(() => () => {
    s.current && (clearTimeout(s.current), s.current = null);
  }, []), [r, g];
}
const er = Zt(({
  height: e,
  value: t,
  className: n,
  style: o,
  themeMode: l,
  onValueChange: r,
  onChange: i,
  slots: s,
  beforeMount: p,
  afterMount: g,
  children: x,
  onMount: u,
  options: k,
  readOnly: v,
  ...O
}) => {
  const P = ye(p), h = ye(g), [M, w] = Yt({
    onValueChange: r,
    value: t
  });
  return /* @__PURE__ */ F.jsxs(F.Fragment, {
    children: [/* @__PURE__ */ F.jsx("div", {
      style: {
        display: "none"
      },
      children: x
    }), /* @__PURE__ */ F.jsx("div", {
      className: n,
      style: {
        ...o,
        height: e
      },
      children: /* @__PURE__ */ F.jsx(Et, {
        ...O,
        value: M,
        beforeMount: P,
        onMount: (...I) => {
          u == null || u(...I), h == null || h(...I);
        },
        options: be(() => ({
          readOnly: v,
          ...k || {}
        }), [k, v]),
        loading: s.loading ? /* @__PURE__ */ F.jsx(It, {
          slot: s.loading
        }) : /* @__PURE__ */ F.jsx(Ae, {
          tip: O.loading,
          wrapperClassName: "ms-gr-pro-monaco-editor-spin",
          children: /* @__PURE__ */ F.jsx("div", {})
        }),
        onChange: (I, d) => {
          w(I), i == null || i(I, d);
        },
        theme: l === "dark" ? "vs-dark" : "light"
      })
    })]
  });
});
export {
  er as MonacoEditor,
  er as default
};
