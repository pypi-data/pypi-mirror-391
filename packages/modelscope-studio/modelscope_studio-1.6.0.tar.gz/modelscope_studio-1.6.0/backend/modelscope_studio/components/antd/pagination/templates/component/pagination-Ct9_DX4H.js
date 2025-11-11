import { i as ae, a as N, r as ue, Z as P, g as de, b as fe } from "./Index-VX8pn35p.js";
const y = window.ms_globals.React, oe = window.ms_globals.React.forwardRef, ie = window.ms_globals.React.useRef, se = window.ms_globals.React.useState, le = window.ms_globals.React.useEffect, ce = window.ms_globals.React.useMemo, F = window.ms_globals.ReactDOM.createPortal, me = window.ms_globals.internalContext.useContextPropsContext, _e = window.ms_globals.internalContext.ContextPropsProvider, he = window.ms_globals.antd.Pagination;
var pe = /\s/;
function ge(e) {
  for (var t = e.length; t-- && pe.test(e.charAt(t)); )
    ;
  return t;
}
var we = /^\s+/;
function be(e) {
  return e && e.slice(0, ge(e) + 1).replace(we, "");
}
var B = NaN, ye = /^[-+]0x[0-9a-f]+$/i, ve = /^0b[01]+$/i, xe = /^0o[0-7]+$/i, Ee = parseInt;
function D(e) {
  if (typeof e == "number")
    return e;
  if (ae(e))
    return B;
  if (N(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = N(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = be(e);
  var o = ve.test(e);
  return o || xe.test(e) ? Ee(e.slice(2), o ? 2 : 8) : ye.test(e) ? B : +e;
}
var j = function() {
  return ue.Date.now();
}, Ce = "Expected a function", Se = Math.max, Ie = Math.min;
function Re(e, t, o) {
  var i, s, n, r, l, u, _ = 0, g = !1, c = !1, w = !0;
  if (typeof e != "function")
    throw new TypeError(Ce);
  t = D(t) || 0, N(o) && (g = !!o.leading, c = "maxWait" in o, n = c ? Se(D(o.maxWait) || 0, t) : n, w = "trailing" in o ? !!o.trailing : w);
  function m(d) {
    var v = i, R = s;
    return i = s = void 0, _ = d, r = e.apply(R, v), r;
  }
  function x(d) {
    return _ = d, l = setTimeout(h, t), g ? m(d) : r;
  }
  function E(d) {
    var v = d - u, R = d - _, z = t - v;
    return c ? Ie(z, n - R) : z;
  }
  function f(d) {
    var v = d - u, R = d - _;
    return u === void 0 || v >= t || v < 0 || c && R >= n;
  }
  function h() {
    var d = j();
    if (f(d))
      return b(d);
    l = setTimeout(h, E(d));
  }
  function b(d) {
    return l = void 0, w && i ? m(d) : (i = s = void 0, r);
  }
  function I() {
    l !== void 0 && clearTimeout(l), _ = 0, i = u = s = l = void 0;
  }
  function a() {
    return l === void 0 ? r : b(j());
  }
  function C() {
    var d = j(), v = f(d);
    if (i = arguments, s = this, u = d, v) {
      if (l === void 0)
        return x(u);
      if (c)
        return clearTimeout(l), l = setTimeout(h, t), m(u);
    }
    return l === void 0 && (l = setTimeout(h, t)), r;
  }
  return C.cancel = I, C.flush = a, C;
}
var Z = {
  exports: {}
}, O = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Pe = y, Te = Symbol.for("react.element"), ke = Symbol.for("react.fragment"), Oe = Object.prototype.hasOwnProperty, je = Pe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Le = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function $(e, t, o) {
  var i, s = {}, n = null, r = null;
  o !== void 0 && (n = "" + o), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (i in t) Oe.call(t, i) && !Le.hasOwnProperty(i) && (s[i] = t[i]);
  if (e && e.defaultProps) for (i in t = e.defaultProps, t) s[i] === void 0 && (s[i] = t[i]);
  return {
    $$typeof: Te,
    type: e,
    key: n,
    ref: r,
    props: s,
    _owner: je.current
  };
}
O.Fragment = ke;
O.jsx = $;
O.jsxs = $;
Z.exports = O;
var p = Z.exports;
const {
  SvelteComponent: Fe,
  assign: U,
  binding_callbacks: G,
  check_outros: Ne,
  children: ee,
  claim_element: te,
  claim_space: We,
  component_subscribe: H,
  compute_slots: Ae,
  create_slot: Me,
  detach: S,
  element: ne,
  empty: J,
  exclude_internal_props: K,
  get_all_dirty_from_scope: ze,
  get_slot_changes: Be,
  group_outros: De,
  init: Ue,
  insert_hydration: T,
  safe_not_equal: Ge,
  set_custom_element_data: re,
  space: He,
  transition_in: k,
  transition_out: W,
  update_slot_base: Je
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ke,
  getContext: Qe,
  onDestroy: qe,
  setContext: Ve
} = window.__gradio__svelte__internal;
function Q(e) {
  let t, o;
  const i = (
    /*#slots*/
    e[7].default
  ), s = Me(
    i,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = ne("svelte-slot"), s && s.c(), this.h();
    },
    l(n) {
      t = te(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = ee(t);
      s && s.l(r), r.forEach(S), this.h();
    },
    h() {
      re(t, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      T(n, t, r), s && s.m(t, null), e[9](t), o = !0;
    },
    p(n, r) {
      s && s.p && (!o || r & /*$$scope*/
      64) && Je(
        s,
        i,
        n,
        /*$$scope*/
        n[6],
        o ? Be(
          i,
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
      o || (k(s, n), o = !0);
    },
    o(n) {
      W(s, n), o = !1;
    },
    d(n) {
      n && S(t), s && s.d(n), e[9](null);
    }
  };
}
function Xe(e) {
  let t, o, i, s, n = (
    /*$$slots*/
    e[4].default && Q(e)
  );
  return {
    c() {
      t = ne("react-portal-target"), o = He(), n && n.c(), i = J(), this.h();
    },
    l(r) {
      t = te(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), ee(t).forEach(S), o = We(r), n && n.l(r), i = J(), this.h();
    },
    h() {
      re(t, "class", "svelte-1rt0kpf");
    },
    m(r, l) {
      T(r, t, l), e[8](t), T(r, o, l), n && n.m(r, l), T(r, i, l), s = !0;
    },
    p(r, [l]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, l), l & /*$$slots*/
      16 && k(n, 1)) : (n = Q(r), n.c(), k(n, 1), n.m(i.parentNode, i)) : n && (De(), W(n, 1, 1, () => {
        n = null;
      }), Ne());
    },
    i(r) {
      s || (k(n), s = !0);
    },
    o(r) {
      W(n), s = !1;
    },
    d(r) {
      r && (S(t), S(o), S(i)), e[8](null), n && n.d(r);
    }
  };
}
function q(e) {
  const {
    svelteInit: t,
    ...o
  } = e;
  return o;
}
function Ye(e, t, o) {
  let i, s, {
    $$slots: n = {},
    $$scope: r
  } = t;
  const l = Ae(n);
  let {
    svelteInit: u
  } = t;
  const _ = P(q(t)), g = P();
  H(e, g, (a) => o(0, i = a));
  const c = P();
  H(e, c, (a) => o(1, s = a));
  const w = [], m = Qe("$$ms-gr-react-wrapper"), {
    slotKey: x,
    slotIndex: E,
    subSlotIndex: f
  } = de() || {}, h = u({
    parent: m,
    props: _,
    target: g,
    slot: c,
    slotKey: x,
    slotIndex: E,
    subSlotIndex: f,
    onDestroy(a) {
      w.push(a);
    }
  });
  Ve("$$ms-gr-react-wrapper", h), Ke(() => {
    _.set(q(t));
  }), qe(() => {
    w.forEach((a) => a());
  });
  function b(a) {
    G[a ? "unshift" : "push"](() => {
      i = a, g.set(i);
    });
  }
  function I(a) {
    G[a ? "unshift" : "push"](() => {
      s = a, c.set(s);
    });
  }
  return e.$$set = (a) => {
    o(17, t = U(U({}, t), K(a))), "svelteInit" in a && o(5, u = a.svelteInit), "$$scope" in a && o(6, r = a.$$scope);
  }, t = K(t), [i, s, g, c, l, u, r, n, b, I];
}
class Ze extends Fe {
  constructor(t) {
    super(), Ue(this, t, Ye, Xe, Ge, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ut
} = window.__gradio__svelte__internal, V = window.ms_globals.rerender, L = window.ms_globals.tree;
function $e(e, t = {}) {
  function o(i) {
    const s = P(), n = new Ze({
      ...i,
      props: {
        svelteInit(r) {
          window.ms_globals.autokey += 1;
          const l = {
            key: window.ms_globals.autokey,
            svelteInstance: s,
            reactComponent: e,
            props: r.props,
            slot: r.slot,
            target: r.target,
            slotIndex: r.slotIndex,
            subSlotIndex: r.subSlotIndex,
            ignore: t.ignore,
            slotKey: r.slotKey,
            nodes: []
          }, u = r.parent ?? L;
          return u.nodes = [...u.nodes, l], V({
            createPortal: F,
            node: L
          }), r.onDestroy(() => {
            u.nodes = u.nodes.filter((_) => _.svelteInstance !== s), V({
              createPortal: F,
              node: L
            });
          }), l;
        },
        ...i.props
      }
    });
    return s.set(n), n;
  }
  return new Promise((i) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((s) => {
      window.ms_globals.initialize = () => {
        s();
      };
    })), window.ms_globals.initializePromise.then(() => {
      i(o);
    });
  });
}
const et = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function tt(e) {
  return e ? Object.keys(e).reduce((t, o) => {
    const i = e[o];
    return t[o] = nt(o, i), t;
  }, {}) : {};
}
function nt(e, t) {
  return typeof t == "number" && !et.includes(e) ? t + "px" : t;
}
function A(e) {
  const t = [], o = e.cloneNode(!1);
  if (e._reactElement) {
    const s = y.Children.toArray(e._reactElement.props.children).map((n) => {
      if (y.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: l
        } = A(n.props.el);
        return y.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...y.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return s.originalChildren = e._reactElement.props.children, t.push(F(y.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: s
    }), o)), {
      clonedElement: o,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((s) => {
    e.getEventListeners(s).forEach(({
      listener: r,
      type: l,
      useCapture: u
    }) => {
      o.addEventListener(l, r, u);
    });
  });
  const i = Array.from(e.childNodes);
  for (let s = 0; s < i.length; s++) {
    const n = i[s];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: l
      } = A(n);
      t.push(...l), o.appendChild(r);
    } else n.nodeType === 3 && o.appendChild(n.cloneNode());
  }
  return {
    clonedElement: o,
    portals: t
  };
}
function rt(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const M = oe(({
  slot: e,
  clone: t,
  className: o,
  style: i,
  observeAttributes: s
}, n) => {
  const r = ie(), [l, u] = se([]), {
    forceClone: _
  } = me(), g = _ ? !0 : t;
  return le(() => {
    var E;
    if (!r.current || !e)
      return;
    let c = e;
    function w() {
      let f = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (f = c.children[0], f.tagName.toLowerCase() === "react-portal-target" && f.children[0] && (f = f.children[0])), rt(n, f), o && f.classList.add(...o.split(" ")), i) {
        const h = tt(i);
        Object.keys(h).forEach((b) => {
          f.style[b] = h[b];
        });
      }
    }
    let m = null, x = null;
    if (g && window.MutationObserver) {
      let f = function() {
        var a, C, d;
        (a = r.current) != null && a.contains(c) && ((C = r.current) == null || C.removeChild(c));
        const {
          portals: b,
          clonedElement: I
        } = A(e);
        c = I, u(b), c.style.display = "contents", x && clearTimeout(x), x = setTimeout(() => {
          w();
        }, 50), (d = r.current) == null || d.appendChild(c);
      };
      f();
      const h = Re(() => {
        f(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: s
        });
      }, 50);
      m = new window.MutationObserver(h), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", w(), (E = r.current) == null || E.appendChild(c);
    return () => {
      var f, h;
      c.style.display = "", (f = r.current) != null && f.contains(c) && ((h = r.current) == null || h.removeChild(c)), m == null || m.disconnect();
    };
  }, [e, g, o, i, n, s, _]), y.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...l);
});
function ot(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function it(e, t = !1) {
  try {
    if (fe(e))
      return e;
    if (t && !ot(e))
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
function X(e, t) {
  return ce(() => it(e, t), [e, t]);
}
const st = ({
  children: e,
  ...t
}) => /* @__PURE__ */ p.jsx(p.Fragment, {
  children: e(t)
});
function lt(e) {
  return y.createElement(st, {
    children: e
  });
}
function Y(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? lt((o) => /* @__PURE__ */ p.jsx(_e, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ p.jsx(M, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...o
    })
  })) : /* @__PURE__ */ p.jsx(M, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function ct({
  key: e,
  slots: t,
  targets: o
}, i) {
  return t[e] ? (...s) => o ? o.map((n, r) => /* @__PURE__ */ p.jsx(y.Fragment, {
    children: Y(n, {
      clone: !0,
      params: s,
      forceClone: (i == null ? void 0 : i.forceClone) ?? !0
    })
  }, r)) : /* @__PURE__ */ p.jsx(p.Fragment, {
    children: Y(t[e], {
      clone: !0,
      params: s,
      forceClone: (i == null ? void 0 : i.forceClone) ?? !0
    })
  }) : void 0;
}
const dt = $e(({
  slots: e,
  showTotal: t,
  showQuickJumper: o,
  onChange: i,
  children: s,
  itemRender: n,
  setSlotParams: r,
  ...l
}) => {
  const u = X(n), _ = X(t);
  return /* @__PURE__ */ p.jsxs(p.Fragment, {
    children: [/* @__PURE__ */ p.jsx("div", {
      style: {
        display: "none"
      },
      children: s
    }), /* @__PURE__ */ p.jsx(he, {
      ...l,
      showTotal: t ? _ : void 0,
      itemRender: e.itemRender ? ct({
        slots: e,
        key: "itemRender"
      }, {}) : u,
      onChange: (g, c) => {
        i == null || i(g, c);
      },
      showQuickJumper: e["showQuickJumper.goButton"] ? {
        goButton: /* @__PURE__ */ p.jsx(M, {
          slot: e["showQuickJumper.goButton"]
        })
      } : o
    })]
  });
});
export {
  dt as Pagination,
  dt as default
};
