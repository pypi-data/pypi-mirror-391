import { i as ue, a as N, r as de, Z as k, g as fe, b as me } from "./Index-CauUQvrs.js";
const I = window.ms_globals.React, ie = window.ms_globals.React.forwardRef, $ = window.ms_globals.React.useRef, ce = window.ms_globals.React.useState, ee = window.ms_globals.React.useEffect, ae = window.ms_globals.React.useMemo, M = window.ms_globals.ReactDOM.createPortal, _e = window.ms_globals.internalContext.useContextPropsContext, he = window.ms_globals.internalContext.ContextPropsProvider, ge = window.ms_globals.antd.Modal;
var pe = /\s/;
function xe(e) {
  for (var t = e.length; t-- && pe.test(e.charAt(t)); )
    ;
  return t;
}
var we = /^\s+/;
function ye(e) {
  return e && e.slice(0, xe(e) + 1).replace(we, "");
}
var D = NaN, be = /^[-+]0x[0-9a-f]+$/i, ve = /^0b[01]+$/i, Ce = /^0o[0-7]+$/i, Ee = parseInt;
function U(e) {
  if (typeof e == "number")
    return e;
  if (ue(e))
    return D;
  if (N(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = N(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = ye(e);
  var o = ve.test(e);
  return o || Ce.test(e) ? Ee(e.slice(2), o ? 2 : 8) : be.test(e) ? D : +e;
}
var L = function() {
  return de.Date.now();
}, Ie = "Expected a function", Pe = Math.max, Se = Math.min;
function Re(e, t, o) {
  var s, l, n, r, i, f, g = 0, x = !1, c = !1, u = !0;
  if (typeof e != "function")
    throw new TypeError(Ie);
  t = U(t) || 0, N(o) && (x = !!o.leading, c = "maxWait" in o, n = c ? Pe(U(o.maxWait) || 0, t) : n, u = "trailing" in o ? !!o.trailing : u);
  function _(d) {
    var w = s, R = l;
    return s = l = void 0, g = d, r = e.apply(R, w), r;
  }
  function b(d) {
    return g = d, i = setTimeout(p, t), x ? _(d) : r;
  }
  function P(d) {
    var w = d - f, R = d - g, z = t - w;
    return c ? Se(z, n - R) : z;
  }
  function m(d) {
    var w = d - f, R = d - g;
    return f === void 0 || w >= t || w < 0 || c && R >= n;
  }
  function p() {
    var d = L();
    if (m(d))
      return y(d);
    i = setTimeout(p, P(d));
  }
  function y(d) {
    return i = void 0, u && s ? _(d) : (s = l = void 0, r);
  }
  function v() {
    i !== void 0 && clearTimeout(i), g = 0, s = f = l = i = void 0;
  }
  function a() {
    return i === void 0 ? r : y(L());
  }
  function C() {
    var d = L(), w = m(d);
    if (s = arguments, l = this, f = d, w) {
      if (i === void 0)
        return b(f);
      if (c)
        return clearTimeout(i), i = setTimeout(p, t), _(f);
    }
    return i === void 0 && (i = setTimeout(p, t)), r;
  }
  return C.cancel = v, C.flush = a, C;
}
var te = {
  exports: {}
}, F = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Te = I, ke = Symbol.for("react.element"), Oe = Symbol.for("react.fragment"), je = Object.prototype.hasOwnProperty, Fe = Te.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Le = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ne(e, t, o) {
  var s, l = {}, n = null, r = null;
  o !== void 0 && (n = "" + o), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (s in t) je.call(t, s) && !Le.hasOwnProperty(s) && (l[s] = t[s]);
  if (e && e.defaultProps) for (s in t = e.defaultProps, t) l[s] === void 0 && (l[s] = t[s]);
  return {
    $$typeof: ke,
    type: e,
    key: n,
    ref: r,
    props: l,
    _owner: Fe.current
  };
}
F.Fragment = Oe;
F.jsx = ne;
F.jsxs = ne;
te.exports = F;
var h = te.exports;
const {
  SvelteComponent: Be,
  assign: H,
  binding_callbacks: G,
  check_outros: Me,
  children: re,
  claim_element: oe,
  claim_space: Ne,
  component_subscribe: K,
  compute_slots: We,
  create_slot: Ae,
  detach: S,
  element: le,
  empty: q,
  exclude_internal_props: J,
  get_all_dirty_from_scope: ze,
  get_slot_changes: De,
  group_outros: Ue,
  init: He,
  insert_hydration: O,
  safe_not_equal: Ge,
  set_custom_element_data: se,
  space: Ke,
  transition_in: j,
  transition_out: W,
  update_slot_base: qe
} = window.__gradio__svelte__internal, {
  beforeUpdate: Je,
  getContext: Xe,
  onDestroy: Ye,
  setContext: Ze
} = window.__gradio__svelte__internal;
function X(e) {
  let t, o;
  const s = (
    /*#slots*/
    e[7].default
  ), l = Ae(
    s,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = le("svelte-slot"), l && l.c(), this.h();
    },
    l(n) {
      t = oe(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = re(t);
      l && l.l(r), r.forEach(S), this.h();
    },
    h() {
      se(t, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      O(n, t, r), l && l.m(t, null), e[9](t), o = !0;
    },
    p(n, r) {
      l && l.p && (!o || r & /*$$scope*/
      64) && qe(
        l,
        s,
        n,
        /*$$scope*/
        n[6],
        o ? De(
          s,
          /*$$scope*/
          n[6],
          r,
          null
        ) : ze(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      o || (j(l, n), o = !0);
    },
    o(n) {
      W(l, n), o = !1;
    },
    d(n) {
      n && S(t), l && l.d(n), e[9](null);
    }
  };
}
function Qe(e) {
  let t, o, s, l, n = (
    /*$$slots*/
    e[4].default && X(e)
  );
  return {
    c() {
      t = le("react-portal-target"), o = Ke(), n && n.c(), s = q(), this.h();
    },
    l(r) {
      t = oe(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), re(t).forEach(S), o = Ne(r), n && n.l(r), s = q(), this.h();
    },
    h() {
      se(t, "class", "svelte-1rt0kpf");
    },
    m(r, i) {
      O(r, t, i), e[8](t), O(r, o, i), n && n.m(r, i), O(r, s, i), l = !0;
    },
    p(r, [i]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, i), i & /*$$slots*/
      16 && j(n, 1)) : (n = X(r), n.c(), j(n, 1), n.m(s.parentNode, s)) : n && (Ue(), W(n, 1, 1, () => {
        n = null;
      }), Me());
    },
    i(r) {
      l || (j(n), l = !0);
    },
    o(r) {
      W(n), l = !1;
    },
    d(r) {
      r && (S(t), S(o), S(s)), e[8](null), n && n.d(r);
    }
  };
}
function Y(e) {
  const {
    svelteInit: t,
    ...o
  } = e;
  return o;
}
function Ve(e, t, o) {
  let s, l, {
    $$slots: n = {},
    $$scope: r
  } = t;
  const i = We(n);
  let {
    svelteInit: f
  } = t;
  const g = k(Y(t)), x = k();
  K(e, x, (a) => o(0, s = a));
  const c = k();
  K(e, c, (a) => o(1, l = a));
  const u = [], _ = Xe("$$ms-gr-react-wrapper"), {
    slotKey: b,
    slotIndex: P,
    subSlotIndex: m
  } = fe() || {}, p = f({
    parent: _,
    props: g,
    target: x,
    slot: c,
    slotKey: b,
    slotIndex: P,
    subSlotIndex: m,
    onDestroy(a) {
      u.push(a);
    }
  });
  Ze("$$ms-gr-react-wrapper", p), Je(() => {
    g.set(Y(t));
  }), Ye(() => {
    u.forEach((a) => a());
  });
  function y(a) {
    G[a ? "unshift" : "push"](() => {
      s = a, x.set(s);
    });
  }
  function v(a) {
    G[a ? "unshift" : "push"](() => {
      l = a, c.set(l);
    });
  }
  return e.$$set = (a) => {
    o(17, t = H(H({}, t), J(a))), "svelteInit" in a && o(5, f = a.svelteInit), "$$scope" in a && o(6, r = a.$$scope);
  }, t = J(t), [s, l, x, c, i, f, r, n, y, v];
}
class $e extends Be {
  constructor(t) {
    super(), He(this, t, Ve, Qe, Ge, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ut
} = window.__gradio__svelte__internal, Z = window.ms_globals.rerender, B = window.ms_globals.tree;
function et(e, t = {}) {
  function o(s) {
    const l = k(), n = new $e({
      ...s,
      props: {
        svelteInit(r) {
          window.ms_globals.autokey += 1;
          const i = {
            key: window.ms_globals.autokey,
            svelteInstance: l,
            reactComponent: e,
            props: r.props,
            slot: r.slot,
            target: r.target,
            slotIndex: r.slotIndex,
            subSlotIndex: r.subSlotIndex,
            ignore: t.ignore,
            slotKey: r.slotKey,
            nodes: []
          }, f = r.parent ?? B;
          return f.nodes = [...f.nodes, i], Z({
            createPortal: M,
            node: B
          }), r.onDestroy(() => {
            f.nodes = f.nodes.filter((g) => g.svelteInstance !== l), Z({
              createPortal: M,
              node: B
            });
          }), i;
        },
        ...s.props
      }
    });
    return l.set(n), n;
  }
  return new Promise((s) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((l) => {
      window.ms_globals.initialize = () => {
        l();
      };
    })), window.ms_globals.initializePromise.then(() => {
      s(o);
    });
  });
}
const tt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function nt(e) {
  return e ? Object.keys(e).reduce((t, o) => {
    const s = e[o];
    return t[o] = rt(o, s), t;
  }, {}) : {};
}
function rt(e, t) {
  return typeof t == "number" && !tt.includes(e) ? t + "px" : t;
}
function A(e) {
  const t = [], o = e.cloneNode(!1);
  if (e._reactElement) {
    const l = I.Children.toArray(e._reactElement.props.children).map((n) => {
      if (I.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: i
        } = A(n.props.el);
        return I.cloneElement(n, {
          ...n.props,
          el: i,
          children: [...I.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return l.originalChildren = e._reactElement.props.children, t.push(M(I.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: l
    }), o)), {
      clonedElement: o,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((l) => {
    e.getEventListeners(l).forEach(({
      listener: r,
      type: i,
      useCapture: f
    }) => {
      o.addEventListener(i, r, f);
    });
  });
  const s = Array.from(e.childNodes);
  for (let l = 0; l < s.length; l++) {
    const n = s[l];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: i
      } = A(n);
      t.push(...i), o.appendChild(r);
    } else n.nodeType === 3 && o.appendChild(n.cloneNode());
  }
  return {
    clonedElement: o,
    portals: t
  };
}
function ot(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const E = ie(({
  slot: e,
  clone: t,
  className: o,
  style: s,
  observeAttributes: l
}, n) => {
  const r = $(), [i, f] = ce([]), {
    forceClone: g
  } = _e(), x = g ? !0 : t;
  return ee(() => {
    var P;
    if (!r.current || !e)
      return;
    let c = e;
    function u() {
      let m = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (m = c.children[0], m.tagName.toLowerCase() === "react-portal-target" && m.children[0] && (m = m.children[0])), ot(n, m), o && m.classList.add(...o.split(" ")), s) {
        const p = nt(s);
        Object.keys(p).forEach((y) => {
          m.style[y] = p[y];
        });
      }
    }
    let _ = null, b = null;
    if (x && window.MutationObserver) {
      let m = function() {
        var a, C, d;
        (a = r.current) != null && a.contains(c) && ((C = r.current) == null || C.removeChild(c));
        const {
          portals: y,
          clonedElement: v
        } = A(e);
        c = v, f(y), c.style.display = "contents", b && clearTimeout(b), b = setTimeout(() => {
          u();
        }, 50), (d = r.current) == null || d.appendChild(c);
      };
      m();
      const p = Re(() => {
        m(), _ == null || _.disconnect(), _ == null || _.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: l
        });
      }, 50);
      _ = new window.MutationObserver(p), _.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", u(), (P = r.current) == null || P.appendChild(c);
    return () => {
      var m, p;
      c.style.display = "", (m = r.current) != null && m.contains(c) && ((p = r.current) == null || p.removeChild(c)), _ == null || _.disconnect();
    };
  }, [e, x, o, s, n, l, g]), I.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...i);
});
function lt(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function st(e, t = !1) {
  try {
    if (me(e))
      return e;
    if (t && !lt(e))
      return;
    if (typeof e == "string") {
      let o = e.trim();
      return o.startsWith(";") && (o = o.slice(1)), o.endsWith(";") && (o = o.slice(0, -1)), new Function(`return (...args) => (${o})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function T(e, t) {
  return ae(() => st(e, t), [e, t]);
}
const it = ({
  children: e,
  ...t
}) => /* @__PURE__ */ h.jsx(h.Fragment, {
  children: e(t)
});
function ct(e) {
  return I.createElement(it, {
    children: e
  });
}
function Q(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? ct((o) => /* @__PURE__ */ h.jsx(he, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ h.jsx(E, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...o
    })
  })) : /* @__PURE__ */ h.jsx(E, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function V({
  key: e,
  slots: t,
  targets: o
}, s) {
  return t[e] ? (...l) => o ? o.map((n, r) => /* @__PURE__ */ h.jsx(I.Fragment, {
    children: Q(n, {
      clone: !0,
      params: l,
      forceClone: !0
    })
  }, r)) : /* @__PURE__ */ h.jsx(h.Fragment, {
    children: Q(t[e], {
      clone: !0,
      params: l,
      forceClone: !0
    })
  }) : void 0;
}
const dt = et(({
  slots: e,
  afterClose: t,
  afterOpenChange: o,
  getContainer: s,
  children: l,
  modalRender: n,
  setSlotParams: r,
  onVisible: i,
  onCancel: f,
  onOk: g,
  visible: x,
  type: c,
  ...u
}) => {
  const _ = T(o), b = T(t), P = T(s), m = T(n), [p, y] = ge.useModal(), v = $(null);
  return ee(() => {
    var a, C, d;
    x ? v.current = p[c || "info"]({
      ...u,
      autoFocusButton: u.autoFocusButton === void 0 ? null : u.autoFocusButton,
      afterOpenChange: _,
      afterClose: b,
      getContainer: typeof s == "string" ? P : s,
      okText: e.okText ? /* @__PURE__ */ h.jsx(E, {
        slot: e.okText
      }) : u.okText,
      okButtonProps: {
        ...u.okButtonProps || {},
        icon: e["okButtonProps.icon"] ? /* @__PURE__ */ h.jsx(E, {
          slot: e["okButtonProps.icon"]
        }) : (a = u.okButtonProps) == null ? void 0 : a.icon
      },
      cancelText: e.cancelText ? /* @__PURE__ */ h.jsx(E, {
        slot: e.cancelText
      }) : u.cancelText,
      cancelButtonProps: {
        ...u.cancelButtonProps || {},
        icon: e["cancelButtonProps.icon"] ? /* @__PURE__ */ h.jsx(E, {
          slot: e["cancelButtonProps.icon"]
        }) : (C = u.cancelButtonProps) == null ? void 0 : C.icon
      },
      closable: e["closable.closeIcon"] ? {
        ...typeof u.closable == "object" ? u.closable : {},
        closeIcon: /* @__PURE__ */ h.jsx(E, {
          slot: e["closable.closeIcon"]
        })
      } : u.closable,
      closeIcon: e.closeIcon ? /* @__PURE__ */ h.jsx(E, {
        slot: e.closeIcon
      }) : u.closeIcon,
      footer: e.footer ? V({
        slots: e,
        key: "footer"
      }) : u.footer,
      title: e.title ? /* @__PURE__ */ h.jsx(E, {
        slot: e.title
      }) : u.title,
      modalRender: e.modalRender ? V({
        slots: e,
        key: "modalRender"
      }) : m,
      onCancel(...w) {
        f == null || f(...w), i == null || i(!1);
      },
      onOk(...w) {
        g == null || g(...w), i == null || i(!1);
      }
    }) : ((d = v.current) == null || d.destroy(), v.current = null);
  }, [x]), /* @__PURE__ */ h.jsxs(h.Fragment, {
    children: [/* @__PURE__ */ h.jsx("div", {
      style: {
        display: "none"
      },
      children: l
    }), y]
  });
});
export {
  dt as ModalStatic,
  dt as default
};
