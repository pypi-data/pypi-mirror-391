import { Z as f, g as G, j as M } from "./Item-DDoeFAyC.js";
const h = window.ms_globals.ReactDOM.createPortal, E = window.ms_globals.createItemsContext.createItemsContext, {
  SvelteComponent: N,
  assign: v,
  binding_callbacks: C,
  check_outros: U,
  children: T,
  claim_element: z,
  claim_space: V,
  component_subscribe: x,
  compute_slots: W,
  create_slot: Z,
  detach: _,
  element: D,
  empty: P,
  exclude_internal_props: y,
  get_all_dirty_from_scope: F,
  get_slot_changes: J,
  group_outros: Q,
  init: X,
  insert_hydration: p,
  safe_not_equal: Y,
  set_custom_element_data: L,
  space: $,
  transition_in: b,
  transition_out: w,
  update_slot_base: ee
} = window.__gradio__svelte__internal, {
  beforeUpdate: te,
  getContext: se,
  onDestroy: oe,
  setContext: ne
} = window.__gradio__svelte__internal;
function k(n) {
  let s, l;
  const r = (
    /*#slots*/
    n[7].default
  ), o = Z(
    r,
    n,
    /*$$scope*/
    n[6],
    null
  );
  return {
    c() {
      s = D("svelte-slot"), o && o.c(), this.h();
    },
    l(e) {
      s = z(e, "SVELTE-SLOT", {
        class: !0
      });
      var t = T(s);
      o && o.l(t), t.forEach(_), this.h();
    },
    h() {
      L(s, "class", "svelte-1rt0kpf");
    },
    m(e, t) {
      p(e, s, t), o && o.m(s, null), n[9](s), l = !0;
    },
    p(e, t) {
      o && o.p && (!l || t & /*$$scope*/
      64) && ee(
        o,
        r,
        e,
        /*$$scope*/
        e[6],
        l ? J(
          r,
          /*$$scope*/
          e[6],
          t,
          null
        ) : F(
          /*$$scope*/
          e[6]
        ),
        null
      );
    },
    i(e) {
      l || (b(o, e), l = !0);
    },
    o(e) {
      w(o, e), l = !1;
    },
    d(e) {
      e && _(s), o && o.d(e), n[9](null);
    }
  };
}
function le(n) {
  let s, l, r, o, e = (
    /*$$slots*/
    n[4].default && k(n)
  );
  return {
    c() {
      s = D("react-portal-target"), l = $(), e && e.c(), r = P(), this.h();
    },
    l(t) {
      s = z(t, "REACT-PORTAL-TARGET", {
        class: !0
      }), T(s).forEach(_), l = V(t), e && e.l(t), r = P(), this.h();
    },
    h() {
      L(s, "class", "svelte-1rt0kpf");
    },
    m(t, a) {
      p(t, s, a), n[8](s), p(t, l, a), e && e.m(t, a), p(t, r, a), o = !0;
    },
    p(t, [a]) {
      /*$$slots*/
      t[4].default ? e ? (e.p(t, a), a & /*$$slots*/
      16 && b(e, 1)) : (e = k(t), e.c(), b(e, 1), e.m(r.parentNode, r)) : e && (Q(), w(e, 1, 1, () => {
        e = null;
      }), U());
    },
    i(t) {
      o || (b(e), o = !0);
    },
    o(t) {
      w(e), o = !1;
    },
    d(t) {
      t && (_(s), _(l), _(r)), n[8](null), e && e.d(t);
    }
  };
}
function S(n) {
  const {
    svelteInit: s,
    ...l
  } = n;
  return l;
}
function re(n, s, l) {
  let r, o, {
    $$slots: e = {},
    $$scope: t
  } = s;
  const a = W(e);
  let {
    svelteInit: c
  } = s;
  const u = f(S(s)), d = f();
  x(n, d, (i) => l(0, r = i));
  const m = f();
  x(n, m, (i) => l(1, o = i));
  const I = [], j = se("$$ms-gr-react-wrapper"), {
    slotKey: A,
    slotIndex: H,
    subSlotIndex: K
  } = G() || {}, O = c({
    parent: j,
    props: u,
    target: d,
    slot: m,
    slotKey: A,
    slotIndex: H,
    subSlotIndex: K,
    onDestroy(i) {
      I.push(i);
    }
  });
  ne("$$ms-gr-react-wrapper", O), te(() => {
    u.set(S(s));
  }), oe(() => {
    I.forEach((i) => i());
  });
  function q(i) {
    C[i ? "unshift" : "push"](() => {
      r = i, d.set(r);
    });
  }
  function B(i) {
    C[i ? "unshift" : "push"](() => {
      o = i, m.set(o);
    });
  }
  return n.$$set = (i) => {
    l(17, s = v(v({}, s), y(i))), "svelteInit" in i && l(5, c = i.svelteInit), "$$scope" in i && l(6, t = i.$$scope);
  }, s = y(s), [r, o, d, m, a, c, t, e, q, B];
}
class ie extends N {
  constructor(s) {
    super(), X(this, s, re, le, Y, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ue
} = window.__gradio__svelte__internal, R = window.ms_globals.rerender, g = window.ms_globals.tree;
function ae(n, s = {}) {
  function l(r) {
    const o = f(), e = new ie({
      ...r,
      props: {
        svelteInit(t) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: n,
            props: t.props,
            slot: t.slot,
            target: t.target,
            slotIndex: t.slotIndex,
            subSlotIndex: t.subSlotIndex,
            ignore: s.ignore,
            slotKey: t.slotKey,
            nodes: []
          }, c = t.parent ?? g;
          return c.nodes = [...c.nodes, a], R({
            createPortal: h,
            node: g
          }), t.onDestroy(() => {
            c.nodes = c.nodes.filter((u) => u.svelteInstance !== o), R({
              createPortal: h,
              node: g
            });
          }), a;
        },
        ...r.props
      }
    });
    return o.set(e), e;
  }
  return new Promise((r) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((o) => {
      window.ms_globals.initialize = () => {
        o();
      };
    })), window.ms_globals.initializePromise.then(() => {
      r(l);
    });
  });
}
const {
  useItems: de,
  withItemsContextProvider: me,
  ItemHandler: ce
} = E("antdx-bubble.list-items"), {
  useItems: fe,
  withItemsContextProvider: pe,
  ItemHandler: be
} = E("antdx-bubble.list-roles"), ge = ae((n) => /* @__PURE__ */ M.jsx(ce, {
  ...n
}));
export {
  ge as BubbleListItem,
  ge as default
};
