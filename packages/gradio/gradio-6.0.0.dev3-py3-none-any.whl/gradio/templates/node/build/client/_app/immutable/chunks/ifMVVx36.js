function create_drag() {
  let hidden_input;
  let _options;
  return {
    drag(node, options = {}) {
      _options = options;
      function setup_hidden_input() {
        hidden_input = document.createElement("input");
        hidden_input.type = "file";
        hidden_input.style.display = "none";
        hidden_input.setAttribute("aria-label", "File upload");
        hidden_input.setAttribute("data-testid", "file-upload");
        const accept_options = Array.isArray(_options.accepted_types) ? _options.accepted_types.join(",") : _options.accepted_types || void 0;
        if (accept_options) {
          hidden_input.accept = accept_options;
        }
        hidden_input.multiple = _options.mode === "multiple" || false;
        if (_options.mode === "directory") {
          hidden_input.webkitdirectory = true;
          hidden_input.setAttribute("directory", "");
          hidden_input.setAttribute("mozdirectory", "");
        }
        node.appendChild(hidden_input);
      }
      setup_hidden_input();
      function handle_drag(e) {
        e.preventDefault();
        e.stopPropagation();
      }
      function handle_drag_enter(e) {
        e.preventDefault();
        e.stopPropagation();
        _options.on_drag_change?.(true);
      }
      function handle_drag_leave(e) {
        e.preventDefault();
        e.stopPropagation();
        _options.on_drag_change?.(false);
      }
      function handle_drop(e) {
        e.preventDefault();
        e.stopPropagation();
        _options.on_drag_change?.(false);
        if (!e.dataTransfer?.files) return;
        const files = Array.from(e.dataTransfer.files);
        if (files.length > 0) {
          _options.on_files?.(files);
        }
      }
      function handle_click() {
        if (!_options.disable_click) {
          hidden_input.value = "";
          hidden_input.click();
        }
      }
      function handle_file_input_change() {
        if (hidden_input.files) {
          const files = Array.from(hidden_input.files);
          if (files.length > 0) {
            _options.on_files?.(files);
          }
        }
      }
      node.addEventListener("drag", handle_drag);
      node.addEventListener("dragstart", handle_drag);
      node.addEventListener("dragend", handle_drag);
      node.addEventListener("dragover", handle_drag);
      node.addEventListener("dragenter", handle_drag_enter);
      node.addEventListener("dragleave", handle_drag_leave);
      node.addEventListener("drop", handle_drop);
      node.addEventListener("click", handle_click);
      hidden_input.addEventListener("change", handle_file_input_change);
      return {
        update(new_options) {
          _options = new_options;
          hidden_input.remove();
          setup_hidden_input();
          hidden_input.addEventListener("change", handle_file_input_change);
        },
        destroy() {
          node.removeEventListener("drag", handle_drag);
          node.removeEventListener("dragstart", handle_drag);
          node.removeEventListener("dragend", handle_drag);
          node.removeEventListener("dragover", handle_drag);
          node.removeEventListener("dragenter", handle_drag_enter);
          node.removeEventListener("dragleave", handle_drag_leave);
          node.removeEventListener("drop", handle_drop);
          node.removeEventListener("click", handle_click);
          hidden_input.removeEventListener("change", handle_file_input_change);
          hidden_input.remove();
        }
      };
    },
    open_file_upload() {
      if (hidden_input) {
        hidden_input.value = "";
        hidden_input.click();
      }
    }
  };
}
export {
  create_drag as c
};
//# sourceMappingURL=ifMVVx36.js.map
