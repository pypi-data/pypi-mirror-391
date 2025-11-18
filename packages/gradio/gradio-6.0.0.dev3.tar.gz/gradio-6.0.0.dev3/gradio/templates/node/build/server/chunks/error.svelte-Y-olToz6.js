import { a7 as escape_html, a3 as getContext } from './async-lbsxUSUV.js';
import { B as BROWSER, D as DEV } from './browser-fallback-CYSLhaFr.js';
import { p as page$3, s as stores } from './client2-BewvQqLI.js';
import './exports-CZNtHRrU.js';

const page$2 = {
  get error() {
    return page$3.error;
  },
  get status() {
    return page$3.status;
  }
};
({
  check: stores.updated.check
});

function context() {
  return getContext("__request__");
}
function context_dev(name) {
  try {
    return context();
  } catch {
    throw new Error(
      `Can only read '${name}' on the server during rendering (not in e.g. \`load\` functions), as it is bound to the current request via component context. This prevents state from leaking between users.For more information, see https://svelte.dev/docs/kit/state-management#avoid-shared-state-on-the-server`
    );
  }
}
const page$1 = {
  get error() {
    return (DEV ? context_dev("page.error") : context()).page.error;
  },
  get status() {
    return (DEV ? context_dev("page.status") : context()).page.status;
  }
};
const page = BROWSER ? page$2 : page$1;
function Error$1($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    $$renderer2.push(`<h1>${escape_html(page.status)}</h1> <p>${escape_html(page.error?.message)}</p>`);
  });
}

export { Error$1 as default };
//# sourceMappingURL=error.svelte-Y-olToz6.js.map
