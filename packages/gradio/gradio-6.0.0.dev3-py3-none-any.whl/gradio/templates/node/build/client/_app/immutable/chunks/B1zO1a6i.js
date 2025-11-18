import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, I as onMount, N as onDestroy, i as legacy_pre_effect, k as get, m as mutable_source, n as legacy_pre_effect_reset, c as from_html, d as child, r as reset, b as append, o as pop, s as sibling, t as template_effect, z as event, j as set, u as deep_read_state, v as first_child, x as derived_safe_equal, y as untrack, g as set_text, q as createEventDispatcher, D as comment, a0 as afterUpdate, K as tick } from "./DEzry6cj.js";
import { p as prop, i as if_block } from "./DUftb7my.js";
import { k as key } from "./DssvUQ9s.js";
import { i as init } from "./DB0xzveP.js";
import { t as each, v as index, s as set_attribute, p as set_style, b as IconButton, a4 as format_time, a as set_class, c as bubble_event, w as set_value, x as prepare_files, N as preventDefault, O as stopPropagation, I as IconButtonWrapper, u as uploadToHuggingFace } from "./DXi4jxVF.js";
import { B as BlockLabel } from "./DEb09X9A.js";
import { D as DownloadLink } from "./BFO3TfnI.js";
import { E as Empty } from "./B-xg5Dhl.js";
import { S as ShareButton } from "./D6EAw2Po.js";
import { D as Download } from "./rkplYKOt.js";
import { V as Video$1 } from "./B7T4xKTK.js";
import { M as Maximize } from "./BS-YSHQt.js";
import { T as Trim, P as Pause } from "./E3gsqwxs.js";
import { P as Play } from "./L86yoUex.js";
import { U as Undo } from "./oKXAgRt1.js";
import { t as trimVideo, b as loadFfmpeg, V as Video } from "./Br4zzvQm.js";
/* empty css         */
import { M as ModifyUpload } from "./BXBtG43Y.js";
var root_1$2 = from_html(`<div class="load-wrap svelte-mctcyk"><span aria-label="loading timeline" class="loader svelte-mctcyk"></span></div>`);
var root_3$2 = from_html(`<img draggable="false" class="svelte-mctcyk"/>`);
var root_2$2 = from_html(`<div id="timeline" class="thumbnail-wrapper svelte-mctcyk"><button aria-label="start drag handle for trimming video" class="handle left svelte-mctcyk"></button> <div class="opaque-layer svelte-mctcyk"></div> <!> <button aria-label="end drag handle for trimming video" class="handle right svelte-mctcyk"></button></div>`);
var root$2 = from_html(`<div class="container svelte-mctcyk"><!></div>`);
function VideoTimeline($$anchor, $$props) {
  push($$props, false);
  let videoElement = prop($$props, "videoElement", 12);
  let trimmedDuration = prop($$props, "trimmedDuration", 12);
  let dragStart = prop($$props, "dragStart", 12);
  let dragEnd = prop($$props, "dragEnd", 12);
  let loadingTimeline = prop($$props, "loadingTimeline", 12);
  let thumbnails = mutable_source([]);
  let numberOfThumbnails = 10;
  let videoDuration;
  let leftHandlePosition = mutable_source(0);
  let rightHandlePosition = mutable_source(100);
  let dragging = null;
  const startDragging = (side) => {
    dragging = side;
  };
  const stopDragging = () => {
    dragging = null;
  };
  const drag = (event2, distance) => {
    if (dragging) {
      const timeline = document.getElementById("timeline");
      if (!timeline) return;
      const rect = timeline.getBoundingClientRect();
      let newPercentage = (event2.clientX - rect.left) / rect.width * 100;
      if (distance) {
        newPercentage = dragging === "left" ? get(leftHandlePosition) + distance : get(rightHandlePosition) + distance;
      } else {
        newPercentage = (event2.clientX - rect.left) / rect.width * 100;
      }
      newPercentage = Math.max(0, Math.min(newPercentage, 100));
      if (dragging === "left") {
        set(leftHandlePosition, Math.min(newPercentage, get(rightHandlePosition)));
        const newTimeLeft = get(leftHandlePosition) / 100 * videoDuration;
        videoElement(videoElement().currentTime = newTimeLeft, true);
        dragStart(newTimeLeft);
      } else if (dragging === "right") {
        set(rightHandlePosition, Math.max(newPercentage, get(leftHandlePosition)));
        const newTimeRight = get(rightHandlePosition) / 100 * videoDuration;
        videoElement(videoElement().currentTime = newTimeRight, true);
        dragEnd(newTimeRight);
      }
      const startTime = get(leftHandlePosition) / 100 * videoDuration;
      const endTime = get(rightHandlePosition) / 100 * videoDuration;
      trimmedDuration(endTime - startTime);
      set(leftHandlePosition, get(leftHandlePosition));
      set(rightHandlePosition, get(rightHandlePosition));
    }
  };
  const moveHandle = (e) => {
    if (dragging) {
      const distance = 1 / videoDuration * 100;
      if (e.key === "ArrowLeft") {
        drag({ clientX: 0 }, -distance);
      } else if (e.key === "ArrowRight") {
        drag({ clientX: 0 }, distance);
      }
    }
  };
  const generateThumbnail = () => {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    canvas.width = videoElement().videoWidth;
    canvas.height = videoElement().videoHeight;
    ctx.drawImage(videoElement(), 0, 0, canvas.width, canvas.height);
    const thumbnail = canvas.toDataURL("image/jpeg", 0.7);
    set(thumbnails, [...get(thumbnails), thumbnail]);
  };
  onMount(() => {
    const loadMetadata = () => {
      videoDuration = videoElement().duration;
      const interval = videoDuration / numberOfThumbnails;
      let captures = 0;
      const onSeeked = () => {
        generateThumbnail();
        captures++;
        if (captures < numberOfThumbnails) {
          videoElement(videoElement().currentTime += interval, true);
        } else {
          videoElement().removeEventListener("seeked", onSeeked);
        }
      };
      videoElement().addEventListener("seeked", onSeeked);
      videoElement(videoElement().currentTime = 0, true);
    };
    if (videoElement().readyState >= 1) {
      loadMetadata();
    } else {
      videoElement().addEventListener("loadedmetadata", loadMetadata);
    }
  });
  onDestroy(() => {
    window.removeEventListener("mousemove", drag);
    window.removeEventListener("mouseup", stopDragging);
    window.removeEventListener("keydown", moveHandle);
  });
  onMount(() => {
    window.addEventListener("mousemove", drag);
    window.addEventListener("mouseup", stopDragging);
    window.addEventListener("keydown", moveHandle);
  });
  legacy_pre_effect(() => get(thumbnails), () => {
    loadingTimeline(get(thumbnails).length !== numberOfThumbnails);
  });
  legacy_pre_effect_reset();
  init();
  var div = root$2();
  var node = child(div);
  {
    var consequent = ($$anchor2) => {
      var div_1 = root_1$2();
      append($$anchor2, div_1);
    };
    var alternate = ($$anchor2) => {
      var div_2 = root_2$2();
      var button = child(div_2);
      var div_3 = sibling(button, 2);
      var node_1 = sibling(div_3, 2);
      each(node_1, 1, () => get(thumbnails), index, ($$anchor3, thumbnail, i) => {
        var img = root_3$2();
        set_attribute(img, "alt", `frame-${i}`);
        template_effect(() => set_attribute(img, "src", get(thumbnail)));
        append($$anchor3, img);
      });
      var button_1 = sibling(node_1, 2);
      reset(div_2);
      template_effect(() => {
        set_style(button, `left: ${get(leftHandlePosition) ?? ""}%;`);
        set_style(div_3, `left: ${get(leftHandlePosition) ?? ""}%; right: ${100 - get(rightHandlePosition)}%`);
        set_style(button_1, `left: ${get(rightHandlePosition) ?? ""}%;`);
      });
      event("mousedown", button, () => startDragging("left"));
      event("blur", button, stopDragging);
      event("keydown", button, (e) => {
        if (e.key === "ArrowLeft" || e.key == "ArrowRight") {
          startDragging("left");
        }
      });
      event("mousedown", button_1, () => startDragging("right"));
      event("blur", button_1, stopDragging);
      event("keydown", button_1, (e) => {
        if (e.key === "ArrowLeft" || e.key == "ArrowRight") {
          startDragging("right");
        }
      });
      append($$anchor2, div_2);
    };
    if_block(node, ($$render) => {
      if (loadingTimeline()) $$render(consequent);
      else $$render(alternate, false);
    });
  }
  reset(div);
  append($$anchor, div);
  pop();
}
var root_1$1 = from_html(`<div class="timeline-wrapper svelte-1orxdv"><!></div>`);
var root_2$1 = from_html(`<time aria-label="duration of selected region in seconds"> </time> <div class="edit-buttons svelte-1orxdv"><button>Trim</button> <button>Cancel</button></div>`, 1);
var root_3$1 = from_html(`<div class="svelte-1orxdv"></div>`);
var root_4 = from_html(`<!> <!>`, 1);
var root$1 = from_html(`<div><!> <div class="controls svelte-1orxdv" data-testid="waveform-controls"><!></div></div> <!>`, 1);
function VideoControls($$anchor, $$props) {
  push($$props, false);
  let videoElement = prop($$props, "videoElement", 8);
  let showRedo = prop($$props, "showRedo", 8, false);
  let interactive = prop($$props, "interactive", 8, true);
  let mode = prop($$props, "mode", 12, "");
  let handle_reset_value = prop($$props, "handle_reset_value", 8);
  let handle_trim_video = prop($$props, "handle_trim_video", 8);
  let processingVideo = prop($$props, "processingVideo", 12, false);
  let i18n = prop($$props, "i18n", 8);
  let value = prop($$props, "value", 8, null);
  let show_download_button = prop($$props, "show_download_button", 8, false);
  let handle_clear = prop($$props, "handle_clear", 8, () => {
  });
  let has_change_history = prop($$props, "has_change_history", 8, false);
  let ffmpeg = mutable_source();
  onMount(async () => {
    set(ffmpeg, await loadFfmpeg());
  });
  let trimmedDuration = mutable_source(null);
  let dragStart = mutable_source(0);
  let dragEnd = mutable_source(0);
  let loadingTimeline = mutable_source(false);
  const toggleTrimmingMode = () => {
    if (mode() === "edit") {
      mode("");
      set(trimmedDuration, videoElement().duration);
    } else {
      mode("edit");
    }
  };
  legacy_pre_effect(
    () => (deep_read_state(mode()), get(trimmedDuration), deep_read_state(videoElement())),
    () => {
      if (mode() === "edit" && get(trimmedDuration) === null && videoElement()) set(trimmedDuration, videoElement().duration);
    }
  );
  legacy_pre_effect_reset();
  init();
  var fragment = root$1();
  var div = first_child(fragment);
  let classes;
  var node = child(div);
  {
    var consequent = ($$anchor2) => {
      var div_1 = root_1$1();
      var node_1 = child(div_1);
      VideoTimeline(node_1, {
        get videoElement() {
          return videoElement();
        },
        get dragStart() {
          return get(dragStart);
        },
        set dragStart($$value) {
          set(dragStart, $$value);
        },
        get dragEnd() {
          return get(dragEnd);
        },
        set dragEnd($$value) {
          set(dragEnd, $$value);
        },
        get trimmedDuration() {
          return get(trimmedDuration);
        },
        set trimmedDuration($$value) {
          set(trimmedDuration, $$value);
        },
        get loadingTimeline() {
          return get(loadingTimeline);
        },
        set loadingTimeline($$value) {
          set(loadingTimeline, $$value);
        },
        $$legacy: true
      });
      reset(div_1);
      append($$anchor2, div_1);
    };
    if_block(node, ($$render) => {
      if (mode() === "edit") $$render(consequent);
    });
  }
  var div_2 = sibling(node, 2);
  var node_2 = child(div_2);
  {
    var consequent_1 = ($$anchor2) => {
      var fragment_1 = root_2$1();
      var time = first_child(fragment_1);
      let classes_1;
      var text = child(time, true);
      reset(time);
      var div_3 = sibling(time, 2);
      var button = child(div_3);
      let classes_2;
      var button_1 = sibling(button, 2);
      let classes_3;
      reset(div_3);
      template_effect(
        ($0) => {
          classes_1 = set_class(time, 1, "svelte-1orxdv", null, classes_1, { hidden: get(loadingTimeline) });
          set_text(text, $0);
          classes_2 = set_class(button, 1, "text-button svelte-1orxdv", null, classes_2, { hidden: get(loadingTimeline) });
          classes_3 = set_class(button_1, 1, "text-button svelte-1orxdv", null, classes_3, { hidden: get(loadingTimeline) });
        },
        [
          () => (deep_read_state(format_time), get(trimmedDuration), untrack(() => format_time(get(trimmedDuration))))
        ]
      );
      event("click", button, () => {
        mode("");
        processingVideo(true);
        trimVideo(get(ffmpeg), get(dragStart), get(dragEnd), videoElement()).then((videoBlob) => {
          handle_trim_video()(videoBlob);
        }).then(() => {
          processingVideo(false);
        });
      });
      event("click", button_1, toggleTrimmingMode);
      append($$anchor2, fragment_1);
    };
    var alternate = ($$anchor2) => {
      var div_4 = root_3$1();
      append($$anchor2, div_4);
    };
    if_block(node_2, ($$render) => {
      if (mode() === "edit" && get(trimmedDuration) !== null) $$render(consequent_1);
      else $$render(alternate, false);
    });
  }
  reset(div_2);
  reset(div);
  var node_3 = sibling(div, 2);
  {
    let $0 = derived_safe_equal(() => (deep_read_state(show_download_button()), deep_read_state(value()), untrack(() => show_download_button() ? value()?.url : null)));
    ModifyUpload(node_3, {
      get i18n() {
        return i18n();
      },
      get download() {
        return get($0);
      },
      $$events: { clear: () => handle_clear()() },
      children: ($$anchor2, $$slotProps) => {
        var fragment_2 = root_4();
        var node_4 = first_child(fragment_2);
        {
          var consequent_2 = ($$anchor3) => {
            {
              let $02 = derived_safe_equal(() => processingVideo() || !has_change_history());
              IconButton($$anchor3, {
                get Icon() {
                  return Undo;
                },
                label: "Reset video to initial value",
                get disabled() {
                  return get($02);
                },
                $$events: {
                  click: () => {
                    handle_reset_value()();
                    mode("");
                  }
                }
              });
            }
          };
          if_block(node_4, ($$render) => {
            if (showRedo() && mode() === "") $$render(consequent_2);
          });
        }
        var node_5 = sibling(node_4, 2);
        {
          var consequent_3 = ($$anchor3) => {
            IconButton($$anchor3, {
              get Icon() {
                return Trim;
              },
              label: "Trim video to selection",
              get disabled() {
                return processingVideo();
              },
              $$events: { click: toggleTrimmingMode }
            });
          };
          if_block(node_5, ($$render) => {
            if (interactive() && mode() === "") $$render(consequent_3);
          });
        }
        append($$anchor2, fragment_2);
      },
      $$slots: { default: true }
    });
  }
  template_effect(() => classes = set_class(div, 1, "container svelte-1orxdv", null, classes, { hidden: mode() !== "edit" }));
  append($$anchor, fragment);
  pop();
}
var root_2 = from_html(`<track kind="captions" default/>`);
var root_1 = from_html(`<div class="wrap svelte-1k28h7x"><div><!></div> <div class="controls svelte-1k28h7x"><div class="inner svelte-1k28h7x"><span role="button" tabindex="0" class="icon svelte-1k28h7x" aria-label="play-pause-replay-button"><!></span> <span class="time svelte-1k28h7x"> </span>  <progress class="svelte-1k28h7x"></progress> <div role="button" tabindex="0" class="icon svelte-1k28h7x" aria-label="full-screen"><!></div></div></div></div> <!>`, 1);
function Player($$anchor, $$props) {
  push($$props, false);
  let root2 = prop($$props, "root", 8, "");
  let src = prop($$props, "src", 8);
  let subtitle = prop($$props, "subtitle", 8, null);
  let mirror = prop($$props, "mirror", 8);
  let autoplay = prop($$props, "autoplay", 8);
  let loop = prop($$props, "loop", 8);
  let label = prop($$props, "label", 8, "test");
  let interactive = prop($$props, "interactive", 8, false);
  let handle_change = prop($$props, "handle_change", 8, () => {
  });
  let handle_reset_value = prop($$props, "handle_reset_value", 8, () => {
  });
  let upload = prop($$props, "upload", 8);
  let is_stream = prop($$props, "is_stream", 8);
  let i18n = prop($$props, "i18n", 8);
  let show_download_button = prop($$props, "show_download_button", 8, false);
  let value = prop($$props, "value", 8, null);
  let handle_clear = prop($$props, "handle_clear", 8, () => {
  });
  let has_change_history = prop($$props, "has_change_history", 8, false);
  const dispatch = createEventDispatcher();
  let time = mutable_source(0);
  let duration = mutable_source();
  let paused = mutable_source(true);
  let video = mutable_source();
  let processingVideo = mutable_source(false);
  function handleMove(e) {
    if (!get(duration)) return;
    if (e.type === "click") {
      handle_click(e);
      return;
    }
    if (e.type !== "touchmove" && !(e.buttons & 1)) return;
    const clientX = e.type === "touchmove" ? e.touches[0].clientX : e.clientX;
    const { left, right } = e.currentTarget.getBoundingClientRect();
    set(time, get(duration) * (clientX - left) / (right - left));
  }
  async function play_pause() {
    if (document.fullscreenElement != get(video)) {
      const isPlaying = get(video).currentTime > 0 && !get(video).paused && !get(video).ended && get(video).readyState > get(video).HAVE_CURRENT_DATA;
      if (!isPlaying) {
        await get(video).play();
      } else get(video).pause();
    }
  }
  function handle_click(e) {
    const { left, right } = e.currentTarget.getBoundingClientRect();
    set(time, get(duration) * (e.clientX - left) / (right - left));
  }
  function handle_end() {
    dispatch("stop");
    dispatch("end");
  }
  const handle_trim_video = async (videoBlob) => {
    let _video_blob = new File([videoBlob], "video.mp4");
    const val = await prepare_files([_video_blob]);
    let value2 = (await upload()(val, root2()))?.filter(Boolean)[0];
    handle_change()(value2);
  };
  function open_full_screen() {
    get(video).requestFullscreen();
  }
  legacy_pre_effect(() => get(time), () => {
    set(time, get(time) || 0);
  });
  legacy_pre_effect(() => get(duration), () => {
    set(duration, get(duration) || 0);
  });
  legacy_pre_effect_reset();
  init();
  var fragment = root_1();
  var div = first_child(fragment);
  var div_1 = child(div);
  let classes;
  var node = child(div_1);
  {
    let $0 = derived_safe_equal(() => `${label()}-player`);
    Video(node, {
      get src() {
        return src();
      },
      preload: "auto",
      get autoplay() {
        return autoplay();
      },
      get loop() {
        return loop();
      },
      get is_stream() {
        return is_stream();
      },
      get "data-testid"() {
        return get($0);
      },
      get processingVideo() {
        return get(processingVideo);
      },
      get currentTime() {
        return get(time);
      },
      set currentTime($$value) {
        set(time, $$value);
      },
      get duration() {
        return get(duration);
      },
      set duration($$value) {
        set(duration, $$value);
      },
      get paused() {
        return get(paused);
      },
      set paused($$value) {
        set(paused, $$value);
      },
      get node() {
        return get(video);
      },
      set node($$value) {
        set(video, $$value);
      },
      $$events: {
        click: play_pause,
        play($$arg) {
          bubble_event.call(this, $$props, $$arg);
        },
        pause($$arg) {
          bubble_event.call(this, $$props, $$arg);
        },
        error($$arg) {
          bubble_event.call(this, $$props, $$arg);
        },
        ended: handle_end,
        loadstart($$arg) {
          bubble_event.call(this, $$props, $$arg);
        },
        loadeddata($$arg) {
          bubble_event.call(this, $$props, $$arg);
        },
        loadedmetadata($$arg) {
          bubble_event.call(this, $$props, $$arg);
        }
      },
      children: ($$anchor2, $$slotProps) => {
        var track = root_2();
        template_effect(() => set_attribute(track, "src", subtitle()));
        append($$anchor2, track);
      },
      $$slots: { default: true },
      $$legacy: true
    });
  }
  reset(div_1);
  var div_2 = sibling(div_1, 2);
  var div_3 = child(div_2);
  var span = child(div_3);
  var node_1 = child(span);
  {
    var consequent = ($$anchor2) => {
      Undo($$anchor2);
    };
    var alternate_1 = ($$anchor2) => {
      var fragment_2 = comment();
      var node_2 = first_child(fragment_2);
      {
        var consequent_1 = ($$anchor3) => {
          Play($$anchor3);
        };
        var alternate = ($$anchor3) => {
          Pause($$anchor3);
        };
        if_block(
          node_2,
          ($$render) => {
            if (get(paused)) $$render(consequent_1);
            else $$render(alternate, false);
          },
          true
        );
      }
      append($$anchor2, fragment_2);
    };
    if_block(node_1, ($$render) => {
      if (get(time) === get(duration)) $$render(consequent);
      else $$render(alternate_1, false);
    });
  }
  reset(span);
  var span_1 = sibling(span, 2);
  var text = child(span_1);
  reset(span_1);
  var progress = sibling(span_1, 2);
  var div_4 = sibling(progress, 2);
  var node_3 = child(div_4);
  Maximize(node_3);
  reset(div_4);
  reset(div_3);
  reset(div_2);
  reset(div);
  var node_4 = sibling(div, 2);
  {
    var consequent_2 = ($$anchor2) => {
      VideoControls($$anchor2, {
        get videoElement() {
          return get(video);
        },
        showRedo: true,
        handle_trim_video,
        get handle_reset_value() {
          return handle_reset_value();
        },
        get value() {
          return value();
        },
        get i18n() {
          return i18n();
        },
        get show_download_button() {
          return show_download_button();
        },
        get handle_clear() {
          return handle_clear();
        },
        get has_change_history() {
          return has_change_history();
        },
        get processingVideo() {
          return get(processingVideo);
        },
        set processingVideo($$value) {
          set(processingVideo, $$value);
        },
        $$legacy: true
      });
    };
    if_block(node_4, ($$render) => {
      if (interactive()) $$render(consequent_2);
    });
  }
  template_effect(
    ($0, $1) => {
      classes = set_class(div_1, 1, "mirror-wrap svelte-1k28h7x", null, classes, { mirror: mirror() });
      set_text(text, `${$0 ?? ""} / ${$1 ?? ""}`);
      set_value(progress, get(time) / get(duration) || 0);
    },
    [
      () => (deep_read_state(format_time), get(time), untrack(() => format_time(get(time)))),
      () => (deep_read_state(format_time), get(duration), untrack(() => format_time(get(duration))))
    ]
  );
  event("click", span, play_pause);
  event("keydown", span, play_pause);
  event("mousemove", progress, handleMove);
  event("touchmove", progress, preventDefault(handleMove));
  event("click", progress, preventDefault(stopPropagation(handle_click)));
  event("click", div_4, open_full_screen);
  event("keypress", div_4, open_full_screen);
  append($$anchor, fragment);
  pop();
}
var root_5 = from_html(`<!> <!>`, 1);
var root_3 = from_html(`<!> <div data-testid="download-div"><!></div>`, 1);
var root = from_html(`<!> <!>`, 1);
function VideoPreview($$anchor, $$props) {
  push($$props, false);
  let value = prop($$props, "value", 12, null);
  let subtitle = prop($$props, "subtitle", 8, null);
  let label = prop($$props, "label", 8, void 0);
  let show_label = prop($$props, "show_label", 8, true);
  let autoplay = prop($$props, "autoplay", 8);
  let show_share_button = prop($$props, "show_share_button", 8, true);
  let show_download_button = prop($$props, "show_download_button", 8, true);
  let loop = prop($$props, "loop", 8);
  let i18n = prop($$props, "i18n", 8);
  let upload = prop($$props, "upload", 8);
  let display_icon_button_wrapper_top_corner = prop($$props, "display_icon_button_wrapper_top_corner", 8, false);
  let old_value = null;
  let old_subtitle = null;
  const dispatch = createEventDispatcher();
  afterUpdate(async () => {
    if (value() !== old_value && subtitle() !== old_subtitle && old_subtitle !== null) {
      old_value = value();
      value(null);
      await tick();
      value(old_value);
    }
    old_value = value();
    old_subtitle = subtitle();
  });
  legacy_pre_effect(() => deep_read_state(value()), () => {
    value() && dispatch("change", value());
  });
  legacy_pre_effect_reset();
  init();
  var fragment = root();
  var node = first_child(fragment);
  {
    let $0 = derived_safe_equal(() => label() || "Video");
    BlockLabel(node, {
      get show_label() {
        return show_label();
      },
      get Icon() {
        return Video$1;
      },
      get label() {
        return get($0);
      }
    });
  }
  var node_1 = sibling(node, 2);
  {
    var consequent = ($$anchor2) => {
      Empty($$anchor2, {
        unpadded_box: true,
        size: "large",
        children: ($$anchor3, $$slotProps) => {
          Video$1($$anchor3);
        },
        $$slots: { default: true }
      });
    };
    var alternate = ($$anchor2) => {
      var fragment_3 = root_3();
      var node_2 = first_child(fragment_3);
      key(node_2, () => (deep_read_state(value()), untrack(() => value().url)), ($$anchor3) => {
        {
          let $0 = derived_safe_equal(() => (deep_read_state(subtitle()), untrack(() => subtitle()?.url)));
          Player($$anchor3, {
            get src() {
              return deep_read_state(value()), untrack(() => value().url);
            },
            get subtitle() {
              return get($0);
            },
            get is_stream() {
              return deep_read_state(value()), untrack(() => value().is_stream);
            },
            get autoplay() {
              return autoplay();
            },
            mirror: false,
            get label() {
              return label();
            },
            get loop() {
              return loop();
            },
            interactive: false,
            get upload() {
              return upload();
            },
            get i18n() {
              return i18n();
            },
            $$events: {
              play($$arg) {
                bubble_event.call(this, $$props, $$arg);
              },
              pause($$arg) {
                bubble_event.call(this, $$props, $$arg);
              },
              stop($$arg) {
                bubble_event.call(this, $$props, $$arg);
              },
              end($$arg) {
                bubble_event.call(this, $$props, $$arg);
              },
              loadedmetadata: () => {
                dispatch("load");
              }
            }
          });
        }
      });
      var div = sibling(node_2, 2);
      var node_3 = child(div);
      IconButtonWrapper(node_3, {
        get display_top_corner() {
          return display_icon_button_wrapper_top_corner();
        },
        children: ($$anchor3, $$slotProps) => {
          var fragment_5 = root_5();
          var node_4 = first_child(fragment_5);
          {
            var consequent_1 = ($$anchor4) => {
              {
                let $0 = derived_safe_equal(() => (deep_read_state(value()), untrack(() => value().is_stream ? value().url?.replace("playlist.m3u8", "playlist-file") : value().url)));
                let $1 = derived_safe_equal(() => (deep_read_state(value()), untrack(() => value().orig_name || value().path)));
                DownloadLink($$anchor4, {
                  get href() {
                    return get($0);
                  },
                  get download() {
                    return get($1);
                  },
                  children: ($$anchor5, $$slotProps2) => {
                    IconButton($$anchor5, {
                      get Icon() {
                        return Download;
                      },
                      label: "Download"
                    });
                  },
                  $$slots: { default: true }
                });
              }
            };
            if_block(node_4, ($$render) => {
              if (show_download_button()) $$render(consequent_1);
            });
          }
          var node_5 = sibling(node_4, 2);
          {
            var consequent_2 = ($$anchor4) => {
              ShareButton($$anchor4, {
                get i18n() {
                  return i18n();
                },
                get value() {
                  return value();
                },
                formatter: async (value2) => {
                  if (!value2) return "";
                  let url = await uploadToHuggingFace(value2.data);
                  return url;
                },
                $$events: {
                  error($$arg) {
                    bubble_event.call(this, $$props, $$arg);
                  },
                  share($$arg) {
                    bubble_event.call(this, $$props, $$arg);
                  }
                }
              });
            };
            if_block(node_5, ($$render) => {
              if (show_share_button()) $$render(consequent_2);
            });
          }
          append($$anchor3, fragment_5);
        },
        $$slots: { default: true }
      });
      reset(div);
      append($$anchor2, fragment_3);
    };
    if_block(node_1, ($$render) => {
      if (deep_read_state(value()), untrack(() => !value() || value().url === void 0)) $$render(consequent);
      else $$render(alternate, false);
    });
  }
  append($$anchor, fragment);
  pop();
}
const VideoPreview$1 = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  default: VideoPreview
}, Symbol.toStringTag, { value: "Module" }));
export {
  Player as P,
  VideoPreview as V,
  VideoPreview$1 as a
};
//# sourceMappingURL=B1zO1a6i.js.map
