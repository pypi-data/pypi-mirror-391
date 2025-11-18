const __vite__mapDeps=(i,m=__vite__mapDeps,d=(m.f||(m.f=["./BJKC1WFY.js","./DkNBN-aT.js","./DLLSm1Xa.js"])))=>i.map(i=>d[i]);
import "./9B4_veAf.js";
import "./BAp-OWo-.js";
import { p as push, q as createEventDispatcher, i as legacy_pre_effect, u as deep_read_state, n as legacy_pre_effect_reset, c as from_html, d as child, y as untrack, r as reset, t as template_effect, b as append, o as pop, g as set_text, D as comment, v as first_child, k as get, I as onMount, N as onDestroy, m as mutable_source, j as set, s as sibling, z as event, Y as mutate, aN as update, x as derived_safe_equal } from "./DEzry6cj.js";
import { p as prop, i as if_block, b as bind_this, _ as __vitePreload } from "./DUftb7my.js";
import { s as slot } from "./DX-MI-YE.js";
import { t as each, v as index, a as set_class, a4 as format_time, p as set_style, k as clsx, x as prepare_files, c as bubble_event } from "./DXi4jxVF.js";
import { i as init } from "./DB0xzveP.js";
import { U as Upload } from "./BcroWaqq.js";
import { M as ModifyUpload } from "./BXBtG43Y.js";
/* empty css         */
import { B as BlockLabel } from "./DEb09X9A.js";
import { M as Music } from "./Dr2P5Z1a.js";
import { S as SelectSource } from "./jPEKutgU.js";
import { StreamingBar } from "./CDyHeC5M.js";
import { s as skip_audio, W as WaveSurfer, a as WaveformControls, p as process_audio, A as AudioPlayer } from "./CxZmGzlA.js";
import { P as Pause } from "./E3gsqwxs.js";
import { S as Spinner } from "./CgQP50mE.js";
function e(e2, t2, i2, s2) {
  return new (i2 || (i2 = Promise))((function(r2, n) {
    function o(e3) {
      try {
        d(s2.next(e3));
      } catch (e4) {
        n(e4);
      }
    }
    function a(e3) {
      try {
        d(s2.throw(e3));
      } catch (e4) {
        n(e4);
      }
    }
    function d(e3) {
      var t3;
      e3.done ? r2(e3.value) : (t3 = e3.value, t3 instanceof i2 ? t3 : new i2((function(e4) {
        e4(t3);
      }))).then(o, a);
    }
    d((s2 = s2.apply(e2, [])).next());
  }));
}
"function" == typeof SuppressedError && SuppressedError;
class t {
  constructor() {
    this.listeners = {}, this.on = this.addEventListener, this.un = this.removeEventListener;
  }
  addEventListener(e2, t2, i2) {
    if (this.listeners[e2] || (this.listeners[e2] = /* @__PURE__ */ new Set()), this.listeners[e2].add(t2), null == i2 ? void 0 : i2.once) {
      const i3 = () => {
        this.removeEventListener(e2, i3), this.removeEventListener(e2, t2);
      };
      return this.addEventListener(e2, i3), i3;
    }
    return () => this.removeEventListener(e2, t2);
  }
  removeEventListener(e2, t2) {
    var i2;
    null === (i2 = this.listeners[e2]) || void 0 === i2 || i2.delete(t2);
  }
  once(e2, t2) {
    return this.on(e2, t2, { once: true });
  }
  unAll() {
    this.listeners = {};
  }
  emit(e2, ...t2) {
    this.listeners[e2] && this.listeners[e2].forEach(((e3) => e3(...t2)));
  }
}
class i extends t {
  constructor(e2) {
    super(), this.subscriptions = [], this.options = e2;
  }
  onInit() {
  }
  init(e2) {
    this.wavesurfer = e2, this.onInit();
  }
  destroy() {
    this.emit("destroy"), this.subscriptions.forEach(((e2) => e2()));
  }
}
const s = ["audio/webm", "audio/wav", "audio/mpeg", "audio/mp4", "audio/mp3"];
class r extends i {
  constructor(e2) {
    var t2;
    super(Object.assign(Object.assign({}, e2), { audioBitsPerSecond: null !== (t2 = e2.audioBitsPerSecond) && void 0 !== t2 ? t2 : 128e3 })), this.stream = null, this.mediaRecorder = null;
  }
  static create(e2) {
    return new r(e2 || {});
  }
  renderMicStream(e2) {
    const t2 = new AudioContext(), i2 = t2.createMediaStreamSource(e2), s2 = t2.createAnalyser();
    i2.connect(s2);
    const r2 = s2.frequencyBinCount, n = new Float32Array(r2), o = r2 / t2.sampleRate;
    let a;
    const d = () => {
      s2.getFloatTimeDomainData(n), this.wavesurfer && (this.wavesurfer.options.cursorWidth = 0, this.wavesurfer.options.interact = false, this.wavesurfer.load("", [n], o)), a = requestAnimationFrame(d);
    };
    return d(), () => {
      cancelAnimationFrame(a), null == i2 || i2.disconnect(), null == t2 || t2.close();
    };
  }
  startMic(t2) {
    return e(this, void 0, void 0, (function* () {
      let e2;
      try {
        e2 = yield navigator.mediaDevices.getUserMedia({ audio: !(null == t2 ? void 0 : t2.deviceId) || { deviceId: t2.deviceId } });
      } catch (e3) {
        throw new Error("Error accessing the microphone: " + e3.message);
      }
      const i2 = this.renderMicStream(e2);
      return this.subscriptions.push(this.once("destroy", i2)), this.stream = e2, e2;
    }));
  }
  stopMic() {
    this.stream && (this.stream.getTracks().forEach(((e2) => e2.stop())), this.stream = null, this.mediaRecorder = null);
  }
  startRecording(t2) {
    return e(this, void 0, void 0, (function* () {
      const e2 = this.stream || (yield this.startMic(t2)), i2 = this.mediaRecorder || new MediaRecorder(e2, { mimeType: this.options.mimeType || s.find(((e3) => MediaRecorder.isTypeSupported(e3))), audioBitsPerSecond: this.options.audioBitsPerSecond });
      this.mediaRecorder = i2, this.stopRecording();
      const r2 = [];
      i2.ondataavailable = (e3) => {
        e3.data.size > 0 && r2.push(e3.data);
      }, i2.onstop = () => {
        var e3;
        const t3 = new Blob(r2, { type: i2.mimeType });
        this.emit("record-end", t3), false !== this.options.renderRecordedAudio && (null === (e3 = this.wavesurfer) || void 0 === e3 || e3.load(URL.createObjectURL(t3)));
      }, i2.start(), this.emit("record-start");
    }));
  }
  isRecording() {
    var e2;
    return "recording" === (null === (e2 = this.mediaRecorder) || void 0 === e2 ? void 0 : e2.state);
  }
  isPaused() {
    var e2;
    return "paused" === (null === (e2 = this.mediaRecorder) || void 0 === e2 ? void 0 : e2.state);
  }
  stopRecording() {
    var e2;
    this.isRecording() && (null === (e2 = this.mediaRecorder) || void 0 === e2 || e2.stop());
  }
  pauseRecording() {
    var e2;
    this.isRecording() && (null === (e2 = this.mediaRecorder) || void 0 === e2 || e2.pause(), this.emit("record-pause"));
  }
  resumeRecording() {
    var e2;
    this.isPaused() && (null === (e2 = this.mediaRecorder) || void 0 === e2 || e2.resume(), this.emit("record-resume"));
  }
  static getAvailableAudioDevices() {
    return e(this, void 0, void 0, (function* () {
      return navigator.mediaDevices.enumerateDevices().then(((e2) => e2.filter(((e3) => "audioinput" === e3.kind))));
    }));
  }
  destroy() {
    super.destroy(), this.stopRecording(), this.stopMic();
  }
}
var root_1$4 = from_html(`<option> </option>`);
var root_3$2 = from_html(`<option> </option>`);
var root$3 = from_html(`<select class="mic-select svelte-ym1wxn" aria-label="Select input device"><!></select>`);
function DeviceSelect($$anchor, $$props) {
  push($$props, false);
  let i18n = prop($$props, "i18n", 8);
  let micDevices = prop($$props, "micDevices", 28, () => []);
  const dispatch = createEventDispatcher();
  legacy_pre_effect(() => deep_read_state(i18n()), () => {
    if (typeof window !== "undefined") {
      try {
        let tempDevices = [];
        r.getAvailableAudioDevices().then((devices) => {
          micDevices(devices);
          devices.forEach((device) => {
            if (device.deviceId) {
              tempDevices.push(device);
            }
          });
          micDevices(tempDevices);
        });
      } catch (err) {
        if (err instanceof DOMException && err.name == "NotAllowedError") {
          dispatch("error", i18n()("audio.allow_recording_access"));
        }
        throw err;
      }
    }
  });
  legacy_pre_effect_reset();
  init();
  var select = root$3();
  var node = child(select);
  {
    var consequent = ($$anchor2) => {
      var option = root_1$4();
      var text = child(option, true);
      reset(option);
      option.value = option.__value = "";
      template_effect(($0) => set_text(text, $0), [
        () => (deep_read_state(i18n()), untrack(() => i18n()("audio.no_microphone")))
      ]);
      append($$anchor2, option);
    };
    var alternate = ($$anchor2) => {
      var fragment = comment();
      var node_1 = first_child(fragment);
      each(node_1, 1, micDevices, index, ($$anchor3, micDevice) => {
        var option_1 = root_3$2();
        var text_1 = child(option_1, true);
        reset(option_1);
        var option_1_value = {};
        template_effect(() => {
          set_text(text_1, (get(micDevice), untrack(() => get(micDevice).label)));
          if (option_1_value !== (option_1_value = (get(micDevice), untrack(() => get(micDevice).deviceId)))) {
            option_1.value = (option_1.__value = (get(micDevice), untrack(() => get(micDevice).deviceId))) ?? "";
          }
        });
        append($$anchor3, option_1);
      });
      append($$anchor2, fragment);
    };
    if_block(node, ($$render) => {
      if (deep_read_state(micDevices()), untrack(() => micDevices().length === 0)) $$render(consequent);
      else $$render(alternate, false);
    });
  }
  reset(select);
  template_effect(() => select.disabled = (deep_read_state(micDevices()), untrack(() => micDevices().length === 0)));
  append($$anchor, select);
  pop();
}
var root_1$3 = from_html(`<time class="duration-button duration svelte-1xuh0j1"> </time>`);
var root$2 = from_html(`<div class="controls svelte-1xuh0j1"><div class="wrapper svelte-1xuh0j1"><button class="record record-button svelte-1xuh0j1"> </button> <button> </button> <button id="stop-paused" class="stop-button-paused svelte-1xuh0j1"> </button> <button aria-label="pause" class="pause-button svelte-1xuh0j1"><!></button> <button class="resume-button svelte-1xuh0j1"> </button> <!></div> <!></div>`);
function WaveformRecordControls($$anchor, $$props) {
  push($$props, false);
  let record = prop($$props, "record", 8);
  let i18n = prop($$props, "i18n", 8);
  let recording = prop($$props, "recording", 8, false);
  let micDevices = mutable_source([]);
  let recordButton = mutable_source();
  let pauseButton = mutable_source();
  let resumeButton = mutable_source();
  let stopButton = mutable_source();
  let stopButtonPaused = mutable_source();
  let recording_ongoing = mutable_source(false);
  let record_time = prop($$props, "record_time", 8);
  let show_recording_waveform = prop($$props, "show_recording_waveform", 8);
  let timing = prop($$props, "timing", 8, false);
  const handleRecordStart = () => {
    mutate(recordButton, get(recordButton).style.display = "none");
    mutate(stopButton, get(stopButton).style.display = "flex");
    mutate(pauseButton, get(pauseButton).style.display = "block");
  };
  const handleRecordEnd = () => {
    if (record().isPaused()) {
      record().resumeRecording();
      record().stopRecording();
    }
    record().stopMic();
    mutate(recordButton, get(recordButton).style.display = "flex");
    mutate(stopButton, get(stopButton).style.display = "none");
    mutate(pauseButton, get(pauseButton).style.display = "none");
    mutate(recordButton, get(recordButton).disabled = false);
  };
  const handleRecordPause = () => {
    mutate(pauseButton, get(pauseButton).style.display = "none");
    mutate(resumeButton, get(resumeButton).style.display = "block");
    mutate(stopButton, get(stopButton).style.display = "none");
    mutate(stopButtonPaused, get(stopButtonPaused).style.display = "flex");
  };
  const handleRecordResume = () => {
    mutate(pauseButton, get(pauseButton).style.display = "block");
    mutate(resumeButton, get(resumeButton).style.display = "none");
    mutate(recordButton, get(recordButton).style.display = "none");
    mutate(stopButton, get(stopButton).style.display = "flex");
    mutate(stopButtonPaused, get(stopButtonPaused).style.display = "none");
  };
  onMount(() => {
    record().on("record-start", handleRecordStart);
    record().on("record-end", handleRecordEnd);
    record().on("record-pause", handleRecordPause);
    record().on("record-resume", handleRecordResume);
  });
  onDestroy(() => {
    record().un("record-start", handleRecordStart);
    record().un("record-end", handleRecordEnd);
    record().un("record-pause", handleRecordPause);
    record().un("record-resume", handleRecordResume);
  });
  legacy_pre_effect(
    () => (deep_read_state(recording()), get(recording_ongoing), deep_read_state(record())),
    () => {
      if (recording() && !get(recording_ongoing)) {
        record().startMic().then(() => {
          record().startRecording();
          set(recording_ongoing, true);
        });
      } else if (!recording() && get(recording_ongoing)) {
        if (record().isPaused()) {
          record().resumeRecording();
        }
        record().stopRecording();
        set(recording_ongoing, false);
      }
    }
  );
  legacy_pre_effect_reset();
  init();
  var div = root$2();
  var div_1 = child(div);
  var button = child(div_1);
  var text = child(button, true);
  reset(button);
  bind_this(button, ($$value) => set(recordButton, $$value), () => get(recordButton));
  var button_1 = sibling(button, 2);
  var text_1 = child(button_1, true);
  reset(button_1);
  bind_this(button_1, ($$value) => set(stopButton, $$value), () => get(stopButton));
  var button_2 = sibling(button_1, 2);
  var text_2 = child(button_2, true);
  reset(button_2);
  bind_this(button_2, ($$value) => set(stopButtonPaused, $$value), () => get(stopButtonPaused));
  var button_3 = sibling(button_2, 2);
  var node = child(button_3);
  Pause(node);
  reset(button_3);
  bind_this(button_3, ($$value) => set(pauseButton, $$value), () => get(pauseButton));
  var button_4 = sibling(button_3, 2);
  var text_3 = child(button_4, true);
  reset(button_4);
  bind_this(button_4, ($$value) => set(resumeButton, $$value), () => get(resumeButton));
  var node_1 = sibling(button_4, 2);
  {
    var consequent = ($$anchor2) => {
      var time = root_1$3();
      var text_4 = child(time, true);
      reset(time);
      template_effect(() => set_text(text_4, record_time()));
      append($$anchor2, time);
    };
    if_block(node_1, ($$render) => {
      if (timing() && !show_recording_waveform()) $$render(consequent);
    });
  }
  reset(div_1);
  var node_2 = sibling(div_1, 2);
  DeviceSelect(node_2, {
    get i18n() {
      return i18n();
    },
    get micDevices() {
      return get(micDevices);
    },
    set micDevices($$value) {
      set(micDevices, $$value);
    },
    $$legacy: true
  });
  reset(div);
  template_effect(
    ($0, $1, $2, $3, $4) => {
      set_text(text, $0);
      set_class(button_1, 1, `stop-button ${$1 ?? ""}`, "svelte-1xuh0j1");
      set_text(text_1, $2);
      set_text(text_2, $3);
      set_text(text_3, $4);
    },
    [
      () => (deep_read_state(i18n()), untrack(() => i18n()("audio.record"))),
      () => (deep_read_state(record()), untrack(() => record().isPaused() ? "stop-button-paused" : "")),
      () => (deep_read_state(i18n()), untrack(() => i18n()("audio.stop"))),
      () => (deep_read_state(i18n()), untrack(() => i18n()("audio.stop"))),
      () => (deep_read_state(i18n()), untrack(() => i18n()("audio.resume")))
    ]
  );
  event("click", button, () => record().startRecording());
  event("click", button_1, () => {
    if (record().isPaused()) {
      record().resumeRecording();
      record().stopRecording();
    }
    record().stopRecording();
  });
  event("click", button_2, () => {
    if (record().isPaused()) {
      record().resumeRecording();
      record().stopRecording();
    }
    record().stopRecording();
  });
  event("click", button_3, () => record().pauseRecording());
  event("click", button_4, () => record().resumeRecording());
  append($$anchor, div);
  pop();
}
var root_2$1 = from_html(`<time class="trim-duration svelte-j9q3sk"> </time>`);
var root_3$1 = from_html(`<time class="duration svelte-j9q3sk"> </time>`);
var root_4$1 = from_html(`<time class="duration svelte-j9q3sk">0:00</time>`);
var root_1$2 = from_html(`<div class="timestamps svelte-j9q3sk"><time class="time svelte-j9q3sk">0:00</time> <div><!> <!></div></div>`);
var root$1 = from_html(`<div class="component-wrapper svelte-j9q3sk"><div class="microphone svelte-j9q3sk" data-testid="microphone-waveform"></div> <div data-testid="recording-waveform"></div> <!> <!> <!></div>`);
function AudioRecorder($$anchor, $$props) {
  push($$props, false);
  let mode = prop($$props, "mode", 12);
  let i18n = prop($$props, "i18n", 8);
  let dispatch_blob = prop($$props, "dispatch_blob", 8);
  let waveform_settings = prop($$props, "waveform_settings", 8);
  let waveform_options = prop($$props, "waveform_options", 24, () => ({ show_recording_waveform: true }));
  let handle_reset_value = prop($$props, "handle_reset_value", 8);
  let editable = prop($$props, "editable", 8, true);
  let recording = prop($$props, "recording", 8, false);
  let micWaveform;
  let recordingWaveform = mutable_source();
  let playing = mutable_source(false);
  let recordingContainer = mutable_source();
  let microphoneContainer = mutable_source();
  let record = mutable_source();
  let recordedAudio = mutable_source(null);
  let timeRef = mutable_source();
  let durationRef = mutable_source();
  let audio_duration = mutable_source();
  let seconds = mutable_source(0);
  let interval;
  let timing = mutable_source(false);
  let trimDuration = mutable_source(0);
  const start_interval = () => {
    clearInterval(interval);
    interval = setInterval(
      () => {
        update(seconds);
      },
      1e3
    );
  };
  const dispatch = createEventDispatcher();
  function record_start_callback() {
    start_interval();
    set(timing, true);
    dispatch("start_recording");
    if (waveform_options().show_recording_waveform) {
      let waveformCanvas = get(microphoneContainer);
      if (waveformCanvas) waveformCanvas.style.display = "block";
    }
  }
  async function record_end_callback(blob) {
    set(seconds, 0);
    set(timing, false);
    clearInterval(interval);
    try {
      const array_buffer = await blob.arrayBuffer();
      const context = new AudioContext({ sampleRate: waveform_settings().sampleRate });
      const audio_buffer = await context.decodeAudioData(array_buffer);
      if (audio_buffer) await process_audio(audio_buffer).then(async (audio) => {
        await dispatch_blob()([audio], "change");
        await dispatch_blob()([audio], "stop_recording");
      });
    } catch (e2) {
      console.error(e2);
    }
  }
  let record_mounted = mutable_source(false);
  const create_mic_waveform = () => {
    if (get(microphoneContainer)) mutate(microphoneContainer, get(microphoneContainer).innerHTML = "");
    if (micWaveform !== void 0) micWaveform.destroy();
    if (!get(microphoneContainer)) return;
    micWaveform = WaveSurfer.create({
      ...waveform_settings(),
      normalize: false,
      container: get(microphoneContainer)
    });
    set(record, micWaveform.registerPlugin(r.create()));
    get(record)?.on("record-end", record_end_callback);
    get(record)?.on("record-start", record_start_callback);
    get(record)?.on("record-pause", () => {
      dispatch("pause_recording");
      clearInterval(interval);
    });
    get(record)?.on("record-end", (blob) => {
      set(recordedAudio, URL.createObjectURL(blob));
      const microphone = get(microphoneContainer);
      const recording2 = get(recordingContainer);
      if (microphone) microphone.style.display = "none";
      if (recording2 && get(recordedAudio)) {
        recording2.innerHTML = "";
        create_recording_waveform();
      }
    });
    set(record_mounted, true);
  };
  const create_recording_waveform = () => {
    let recording2 = get(recordingContainer);
    if (!get(recordedAudio) || !recording2) return;
    set(recordingWaveform, WaveSurfer.create({
      container: recording2,
      url: get(recordedAudio),
      ...waveform_settings()
    }));
  };
  const handle_trim_audio = async (start, end) => {
    mode("edit");
    const decodedData = get(recordingWaveform).getDecodedData();
    if (decodedData) await process_audio(decodedData, start, end).then(async (trimmedAudio) => {
      await dispatch_blob()([trimmedAudio], "change");
      await dispatch_blob()([trimmedAudio], "stop_recording");
      get(recordingWaveform).destroy();
      create_recording_waveform();
    });
    dispatch("edit");
  };
  onMount(() => {
    create_mic_waveform();
    window.addEventListener("keydown", (e2) => {
      const is_focused_in_waveform = get(recordingContainer) && get(recordingContainer).contains(document.activeElement);
      if (!is_focused_in_waveform) return;
      if (e2.key === "ArrowRight") {
        skip_audio(get(recordingWaveform), 0.1);
      } else if (e2.key === "ArrowLeft") {
        skip_audio(get(recordingWaveform), -0.1);
      }
    });
  });
  legacy_pre_effect(() => get(record), () => {
    get(record)?.on("record-resume", () => {
      start_interval();
    });
  });
  legacy_pre_effect(() => (get(recordingWaveform), get(durationRef), format_time), () => {
    get(recordingWaveform)?.on("decode", (duration) => {
      set(audio_duration, duration);
      get(durationRef) && mutate(durationRef, get(durationRef).textContent = format_time(duration));
    });
  });
  legacy_pre_effect(() => (get(recordingWaveform), get(timeRef), format_time), () => {
    get(recordingWaveform)?.on("timeupdate", (currentTime) => get(timeRef) && mutate(timeRef, get(timeRef).textContent = format_time(currentTime)));
  });
  legacy_pre_effect(() => get(recordingWaveform), () => {
    get(recordingWaveform)?.on("pause", () => {
      dispatch("pause");
      set(playing, false);
    });
  });
  legacy_pre_effect(() => get(recordingWaveform), () => {
    get(recordingWaveform)?.on("play", () => {
      dispatch("play");
      set(playing, true);
    });
  });
  legacy_pre_effect(() => get(recordingWaveform), () => {
    get(recordingWaveform)?.on("finish", () => {
      dispatch("stop");
      set(playing, false);
    });
  });
  legacy_pre_effect_reset();
  init();
  var div = root$1();
  var div_1 = child(div);
  bind_this(div_1, ($$value) => set(microphoneContainer, $$value), () => get(microphoneContainer));
  var div_2 = sibling(div_1, 2);
  bind_this(div_2, ($$value) => set(recordingContainer, $$value), () => get(recordingContainer));
  var node = sibling(div_2, 2);
  {
    var consequent_2 = ($$anchor2) => {
      var div_3 = root_1$2();
      var time = child(div_3);
      bind_this(time, ($$value) => set(timeRef, $$value), () => get(timeRef));
      var div_4 = sibling(time, 2);
      var node_1 = child(div_4);
      {
        var consequent = ($$anchor3) => {
          var time_1 = root_2$1();
          var text = child(time_1, true);
          reset(time_1);
          template_effect(($0) => set_text(text, $0), [
            () => (deep_read_state(format_time), get(trimDuration), untrack(() => format_time(get(trimDuration))))
          ]);
          append($$anchor3, time_1);
        };
        if_block(node_1, ($$render) => {
          if (mode() === "edit" && get(trimDuration) > 0) $$render(consequent);
        });
      }
      var node_2 = sibling(node_1, 2);
      {
        var consequent_1 = ($$anchor3) => {
          var time_2 = root_3$1();
          var text_1 = child(time_2, true);
          reset(time_2);
          template_effect(($0) => set_text(text_1, $0), [
            () => (deep_read_state(format_time), get(seconds), untrack(() => format_time(get(seconds))))
          ]);
          append($$anchor3, time_2);
        };
        var alternate = ($$anchor3) => {
          var time_3 = root_4$1();
          bind_this(time_3, ($$value) => set(durationRef, $$value), () => get(durationRef));
          append($$anchor3, time_3);
        };
        if_block(node_2, ($$render) => {
          if (get(timing)) $$render(consequent_1);
          else $$render(alternate, false);
        });
      }
      reset(div_4);
      reset(div_3);
      append($$anchor2, div_3);
    };
    if_block(node, ($$render) => {
      if (get(timing), get(recordedAudio), deep_read_state(waveform_options()), untrack(() => (get(timing) || get(recordedAudio)) && waveform_options().show_recording_waveform)) $$render(consequent_2);
    });
  }
  var node_3 = sibling(node, 2);
  {
    var consequent_3 = ($$anchor2) => {
      {
        let $0 = derived_safe_equal(() => (deep_read_state(format_time), get(seconds), untrack(() => format_time(get(seconds)))));
        WaveformRecordControls($$anchor2, {
          get i18n() {
            return i18n();
          },
          get timing() {
            return get(timing);
          },
          get recording() {
            return recording();
          },
          get show_recording_waveform() {
            return deep_read_state(waveform_options()), untrack(() => waveform_options().show_recording_waveform);
          },
          get record_time() {
            return get($0);
          },
          get record() {
            return get(record);
          },
          set record($$value) {
            set(record, $$value);
          },
          $$legacy: true
        });
      }
    };
    if_block(node_3, ($$render) => {
      if (get(microphoneContainer) && !get(recordedAudio) && get(record_mounted)) $$render(consequent_3);
    });
  }
  var node_4 = sibling(node_3, 2);
  {
    var consequent_4 = ($$anchor2) => {
      WaveformControls($$anchor2, {
        get container() {
          return get(recordingContainer);
        },
        get playing() {
          return get(playing);
        },
        get audio_duration() {
          return get(audio_duration);
        },
        get i18n() {
          return i18n();
        },
        get editable() {
          return editable();
        },
        interactive: true,
        handle_trim_audio,
        show_redo: true,
        get handle_reset_value() {
          return handle_reset_value();
        },
        get waveform_options() {
          return waveform_options();
        },
        get waveform() {
          return get(recordingWaveform);
        },
        set waveform($$value) {
          set(recordingWaveform, $$value);
        },
        get trimDuration() {
          return get(trimDuration);
        },
        set trimDuration($$value) {
          set(trimDuration, $$value);
        },
        get mode() {
          return mode();
        },
        set mode($$value) {
          mode($$value);
        },
        $$legacy: true
      });
    };
    if_block(node_4, ($$render) => {
      if (get(recordingWaveform) && get(recordedAudio)) $$render(consequent_4);
    });
  }
  reset(div);
  append($$anchor, div);
  pop();
}
var root_1$1 = from_html(`<div class="svelte-m6ymia"></div>`);
var root_2 = from_html(`<button><span class="record-icon svelte-m6ymia"><span class="pinger svelte-m6ymia"></span> <span class="dot svelte-m6ymia"></span></span> </button>`);
var root_4 = from_html(`<button class="spinner-button svelte-m6ymia"><div class="icon svelte-m6ymia"><!></div> </button>`);
var root_5 = from_html(`<button class="record-button svelte-m6ymia"><span class="record-icon svelte-m6ymia"><span class="dot svelte-m6ymia"></span></span> </button>`);
var root = from_html(`<div class="mic-wrap svelte-m6ymia"><!> <div class="controls svelte-m6ymia"><!> <!></div></div>`);
function StreamAudio($$anchor, $$props) {
  push($$props, false);
  let recording = prop($$props, "recording", 8, false);
  let paused_recording = prop($$props, "paused_recording", 8, false);
  let stop = prop($$props, "stop", 8);
  let record = prop($$props, "record", 8);
  let i18n = prop($$props, "i18n", 8);
  let waveform_settings = prop($$props, "waveform_settings", 8);
  let waveform_options = prop($$props, "waveform_options", 24, () => ({ show_recording_waveform: true }));
  let waiting = prop($$props, "waiting", 8, false);
  let micWaveform;
  let waveformRecord = mutable_source();
  let microphoneContainer = mutable_source();
  let micDevices = mutable_source([]);
  onMount(() => {
    create_mic_waveform();
  });
  const create_mic_waveform = () => {
    if (micWaveform !== void 0) micWaveform.destroy();
    if (!get(microphoneContainer)) return;
    micWaveform = WaveSurfer.create({
      ...waveform_settings(),
      normalize: false,
      container: get(microphoneContainer)
    });
    set(waveformRecord, micWaveform.registerPlugin(r.create()));
  };
  init();
  var div = root();
  var node = child(div);
  {
    var consequent = ($$anchor2) => {
      var div_1 = root_1$1();
      let styles;
      bind_this(div_1, ($$value) => set(microphoneContainer, $$value), () => get(microphoneContainer));
      template_effect(() => styles = set_style(div_1, "", styles, { display: recording() ? "block" : "none" }));
      append($$anchor2, div_1);
    };
    if_block(node, ($$render) => {
      if (deep_read_state(waveform_options()), untrack(() => waveform_options().show_recording_waveform)) $$render(consequent);
    });
  }
  var div_2 = sibling(node, 2);
  var node_1 = child(div_2);
  {
    var consequent_1 = ($$anchor2) => {
      var button = root_2();
      var text = sibling(child(button));
      reset(button);
      template_effect(
        ($0) => {
          set_class(button, 1, clsx(paused_recording() ? "stop-button-paused" : "stop-button"), "svelte-m6ymia");
          set_text(text, ` ${$0 ?? ""}`);
        },
        [
          () => (deep_read_state(paused_recording()), deep_read_state(i18n()), untrack(() => paused_recording() ? i18n()("audio.pause") : i18n()("audio.stop")))
        ]
      );
      event("click", button, () => {
        get(waveformRecord)?.stopMic();
        stop()();
      });
      append($$anchor2, button);
    };
    var alternate_1 = ($$anchor2) => {
      var fragment = comment();
      var node_2 = first_child(fragment);
      {
        var consequent_2 = ($$anchor3) => {
          var button_1 = root_4();
          var div_3 = child(button_1);
          var node_3 = child(div_3);
          Spinner(node_3);
          reset(div_3);
          var text_1 = sibling(div_3);
          reset(button_1);
          template_effect(($0) => set_text(text_1, ` ${$0 ?? ""}`), [
            () => (deep_read_state(i18n()), untrack(() => i18n()("audio.waiting")))
          ]);
          event("click", button_1, () => {
            stop()();
          });
          append($$anchor3, button_1);
        };
        var alternate = ($$anchor3) => {
          var button_2 = root_5();
          var text_2 = sibling(child(button_2));
          reset(button_2);
          template_effect(($0) => set_text(text_2, ` ${$0 ?? ""}`), [
            () => (deep_read_state(i18n()), untrack(() => i18n()("audio.record")))
          ]);
          event("click", button_2, () => {
            get(waveformRecord)?.startMic();
            record()();
          });
          append($$anchor3, button_2);
        };
        if_block(
          node_2,
          ($$render) => {
            if (recording() && waiting()) $$render(consequent_2);
            else $$render(alternate, false);
          },
          true
        );
      }
      append($$anchor2, fragment);
    };
    if_block(node_1, ($$render) => {
      if (recording() && !waiting()) $$render(consequent_1);
      else $$render(alternate_1, false);
    });
  }
  var node_4 = sibling(node_1, 2);
  DeviceSelect(node_4, {
    get i18n() {
      return i18n();
    },
    get micDevices() {
      return get(micDevices);
    },
    set micDevices($$value) {
      set(micDevices, $$value);
    },
    $$legacy: true
  });
  reset(div_2);
  reset(div);
  append($$anchor, div);
  pop();
}
let media_recorder;
async function init_media_recorder() {
  const { MediaRecorder: MediaRecorder2, register } = await __vitePreload(async () => {
    const { MediaRecorder: MediaRecorder3, register: register2 } = await import("./BJKC1WFY.js");
    return { MediaRecorder: MediaRecorder3, register: register2 };
  }, true ? __vite__mapDeps([0,1]) : void 0, import.meta.url);
  const { connect } = await __vitePreload(async () => {
    const { connect: connect2 } = await import("./DLLSm1Xa.js");
    return { connect: connect2 };
  }, true ? __vite__mapDeps([2,1]) : void 0, import.meta.url);
  register(await connect());
  media_recorder = MediaRecorder2;
  return media_recorder;
}
var root_3 = from_html(`<!> <!>`, 1);
var root_9 = from_html(`<!> <!>`, 1);
var root_1 = from_html(`<!> <div><!> <!> <!></div>`, 1);
function InteractiveAudio($$anchor, $$props) {
  push($$props, false);
  let value = prop($$props, "value", 12, null);
  let subtitles = prop($$props, "subtitles", 8, null);
  let label = prop($$props, "label", 8);
  let root2 = prop($$props, "root", 8);
  let loop = prop($$props, "loop", 8);
  let show_label = prop($$props, "show_label", 8, true);
  let buttons = prop($$props, "buttons", 24, () => ["download", "share"]);
  let sources = prop($$props, "sources", 24, () => ["microphone", "upload"]);
  let pending = prop($$props, "pending", 8, false);
  let streaming = prop($$props, "streaming", 8, false);
  let i18n = prop($$props, "i18n", 8);
  let waveform_settings = prop($$props, "waveform_settings", 8);
  let trim_region_settings = prop($$props, "trim_region_settings", 24, () => ({}));
  let waveform_options = prop($$props, "waveform_options", 24, () => ({}));
  let dragging = prop($$props, "dragging", 12);
  let active_source = prop($$props, "active_source", 12);
  let handle_reset_value = prop($$props, "handle_reset_value", 8, () => {
  });
  let editable = prop($$props, "editable", 8, true);
  let max_file_size = prop($$props, "max_file_size", 8, null);
  let upload = prop($$props, "upload", 8);
  let stream_handler = prop($$props, "stream_handler", 8);
  let stream_every = prop($$props, "stream_every", 8, 0.1);
  let uploading = prop($$props, "uploading", 12, false);
  let recording = prop($$props, "recording", 12, false);
  let class_name = prop($$props, "class_name", 8, "");
  let upload_promise = prop($$props, "upload_promise", 12, null);
  let initial_value = prop($$props, "initial_value", 12, null);
  let time_limit = prop($$props, "time_limit", 8, null);
  let stream_state = prop($$props, "stream_state", 8, "closed");
  let recorder = mutable_source();
  let mode = mutable_source("");
  let header = mutable_source(void 0);
  let pending_stream = mutable_source([]);
  let submit_pending_stream_on_pending_end = mutable_source(false);
  let inited = false;
  let streaming_media_recorder;
  const NUM_HEADER_BYTES = 44;
  let audio_chunks = [];
  const is_browser = typeof window !== "undefined";
  if (is_browser && streaming()) {
    init_media_recorder().then((a) => {
      streaming_media_recorder = a;
    });
  }
  const dispatch = createEventDispatcher();
  const dispatch_blob = async (blobs, event2) => {
    let _audio_blob = new File(blobs, "audio.wav");
    const val = await prepare_files([_audio_blob], event2 === "stream");
    initial_value(value());
    value((await upload()(val, root2(), void 0, max_file_size() || void 0))?.filter(Boolean)[0]);
    dispatch(event2, value());
  };
  onDestroy(() => {
    if (streaming() && get(recorder) && get(recorder).state !== "inactive") {
      get(recorder).stop();
    }
  });
  async function prepare_audio() {
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (err) {
      if (!navigator.mediaDevices) {
        dispatch("error", i18n()("audio.no_device_support"));
        return;
      }
      if (err instanceof DOMException && err.name == "NotAllowedError") {
        dispatch("error", i18n()("audio.allow_recording_access"));
        return;
      }
      throw err;
    }
    if (stream == null) return;
    if (streaming()) {
      set(recorder, new streaming_media_recorder(stream, { mimeType: "audio/wav" }));
      get(recorder).addEventListener("dataavailable", handle_chunk);
    } else {
      set(recorder, new MediaRecorder(stream));
      get(recorder).addEventListener("dataavailable", (event2) => {
        audio_chunks.push(event2.data);
      });
    }
    get(recorder).addEventListener("stop", async () => {
      recording(false);
      await dispatch_blob(audio_chunks, "change");
      await dispatch_blob(audio_chunks, "stop_recording");
      audio_chunks = [];
    });
    inited = true;
  }
  async function handle_chunk(event2) {
    let buffer = await event2.data.arrayBuffer();
    let payload = new Uint8Array(buffer);
    if (!get(header)) {
      set(header, new Uint8Array(buffer.slice(0, NUM_HEADER_BYTES)));
      payload = new Uint8Array(buffer.slice(NUM_HEADER_BYTES));
    }
    if (pending()) {
      get(pending_stream).push(payload);
    } else {
      let blobParts = [get(header)].concat(get(pending_stream), [payload]);
      if (!recording() || stream_state() === "waiting") return;
      dispatch_blob(blobParts, "stream");
      set(pending_stream, []);
    }
  }
  async function record() {
    recording(true);
    dispatch("start_recording");
    if (!inited) await prepare_audio();
    set(header, void 0);
    if (streaming() && get(recorder).state != "recording") {
      get(recorder).start(stream_every() * 1e3);
    }
  }
  function clear() {
    dispatch("change", null);
    dispatch("clear");
    set(mode, "");
    value(null);
  }
  function handle_load({ detail }) {
    value(detail);
    dispatch("change", detail);
    dispatch("upload", detail);
  }
  async function stop() {
    recording(false);
    if (streaming()) {
      dispatch("close_stream");
      dispatch("stop_recording");
      get(recorder).stop();
      if (pending()) {
        set(submit_pending_stream_on_pending_end, true);
      }
      dispatch_blob(audio_chunks, "stop_recording");
      dispatch("clear");
      set(mode, "");
    }
  }
  legacy_pre_effect(() => deep_read_state(dragging()), () => {
    dispatch("drag", dragging());
  });
  legacy_pre_effect(
    () => (get(submit_pending_stream_on_pending_end), deep_read_state(pending()), get(header), get(pending_stream)),
    () => {
      if (get(submit_pending_stream_on_pending_end) && pending() === false) {
        set(submit_pending_stream_on_pending_end, false);
        if (get(header) && get(pending_stream)) {
          let blobParts = [get(header)].concat(get(pending_stream));
          set(pending_stream, []);
          dispatch_blob(blobParts, "stream");
        }
      }
    }
  );
  legacy_pre_effect(() => (deep_read_state(recording()), get(recorder)), () => {
    if (!recording() && get(recorder)) stop();
  });
  legacy_pre_effect(() => (deep_read_state(recording()), get(recorder)), () => {
    if (recording() && get(recorder)) record();
  });
  legacy_pre_effect_reset();
  init();
  var fragment = root_1();
  var node = first_child(fragment);
  {
    let $0 = derived_safe_equal(() => active_source() === "upload" && value() === null);
    let $1 = derived_safe_equal(() => (deep_read_state(label()), deep_read_state(i18n()), untrack(() => label() || i18n()("audio.audio"))));
    BlockLabel(node, {
      get show_label() {
        return show_label();
      },
      get Icon() {
        return Music;
      },
      get float() {
        return get($0);
      },
      get label() {
        return get($1);
      }
    });
  }
  var div = sibling(node, 2);
  var node_1 = child(div);
  StreamingBar(node_1, {
    get time_limit() {
      return time_limit();
    }
  });
  var node_2 = sibling(node_1, 2);
  {
    var consequent_3 = ($$anchor2) => {
      var fragment_1 = comment();
      var node_3 = first_child(fragment_1);
      {
        var consequent_1 = ($$anchor3) => {
          var fragment_2 = root_3();
          var node_4 = first_child(fragment_2);
          ModifyUpload(node_4, {
            get i18n() {
              return i18n();
            },
            $$events: { clear }
          });
          var node_5 = sibling(node_4, 2);
          {
            var consequent = ($$anchor4) => {
              {
                let $0 = derived_safe_equal(() => stream_state() === "waiting");
                StreamAudio($$anchor4, {
                  record,
                  get recording() {
                    return recording();
                  },
                  stop,
                  get i18n() {
                    return i18n();
                  },
                  get waveform_settings() {
                    return waveform_settings();
                  },
                  get waveform_options() {
                    return waveform_options();
                  },
                  get waiting() {
                    return get($0);
                  }
                });
              }
            };
            var alternate = ($$anchor4) => {
              AudioRecorder($$anchor4, {
                get i18n() {
                  return i18n();
                },
                get editable() {
                  return editable();
                },
                get recording() {
                  return recording();
                },
                dispatch_blob,
                get waveform_settings() {
                  return waveform_settings();
                },
                get waveform_options() {
                  return waveform_options();
                },
                get handle_reset_value() {
                  return handle_reset_value();
                },
                get mode() {
                  return get(mode);
                },
                set mode($$value) {
                  set(mode, $$value);
                },
                $$events: {
                  start_recording($$arg) {
                    bubble_event.call(this, $$props, $$arg);
                  },
                  pause_recording($$arg) {
                    bubble_event.call(this, $$props, $$arg);
                  },
                  stop_recording($$arg) {
                    bubble_event.call(this, $$props, $$arg);
                  }
                },
                $$legacy: true
              });
            };
            if_block(node_5, ($$render) => {
              if (streaming()) $$render(consequent);
              else $$render(alternate, false);
            });
          }
          append($$anchor3, fragment_2);
        };
        var alternate_1 = ($$anchor3) => {
          var fragment_5 = comment();
          var node_6 = first_child(fragment_5);
          {
            var consequent_2 = ($$anchor4) => {
              {
                let $0 = derived_safe_equal(() => (deep_read_state(i18n()), untrack(() => i18n()("audio.drop_to_upload"))));
                Upload($$anchor4, {
                  filetype: "audio/aac,audio/midi,audio/mpeg,audio/ogg,audio/wav,audio/x-wav,audio/opus,audio/webm,audio/flac,audio/vnd.rn-realaudio,audio/x-ms-wma,audio/x-aiff,audio/amr,audio/*",
                  get root() {
                    return root2();
                  },
                  get max_file_size() {
                    return max_file_size();
                  },
                  get upload() {
                    return upload();
                  },
                  get stream_handler() {
                    return stream_handler();
                  },
                  get aria_label() {
                    return get($0);
                  },
                  get upload_promise() {
                    return upload_promise();
                  },
                  set upload_promise($$value) {
                    upload_promise($$value);
                  },
                  get dragging() {
                    return dragging();
                  },
                  set dragging($$value) {
                    dragging($$value);
                  },
                  get uploading() {
                    return uploading();
                  },
                  set uploading($$value) {
                    uploading($$value);
                  },
                  $$events: {
                    load: handle_load,
                    error: ({ detail }) => dispatch("error", detail)
                  },
                  children: ($$anchor5, $$slotProps) => {
                    var fragment_7 = comment();
                    var node_7 = first_child(fragment_7);
                    slot(node_7, $$props, "default", {}, null);
                    append($$anchor5, fragment_7);
                  },
                  $$slots: { default: true },
                  $$legacy: true
                });
              }
            };
            if_block(
              node_6,
              ($$render) => {
                if (active_source() === "upload") $$render(consequent_2);
              },
              true
            );
          }
          append($$anchor3, fragment_5);
        };
        if_block(node_3, ($$render) => {
          if (active_source() === "microphone") $$render(consequent_1);
          else $$render(alternate_1, false);
        });
      }
      append($$anchor2, fragment_1);
    };
    var alternate_2 = ($$anchor2) => {
      var fragment_8 = root_9();
      var node_8 = first_child(fragment_8);
      {
        let $0 = derived_safe_equal(() => (deep_read_state(buttons()), deep_read_state(value()), untrack(() => buttons() === null ? value().url : buttons().includes("download") ? value().url : null)));
        ModifyUpload(node_8, {
          get i18n() {
            return i18n();
          },
          get download() {
            return get($0);
          },
          $$events: { clear, edit: () => set(mode, "edit") }
        });
      }
      var node_9 = sibling(node_8, 2);
      {
        let $0 = derived_safe_equal(() => (deep_read_state(subtitles()), untrack(() => Array.isArray(subtitles()) ? subtitles() : subtitles()?.url)));
        AudioPlayer(node_9, {
          get value() {
            return value();
          },
          get subtitles() {
            return get($0);
          },
          get label() {
            return label();
          },
          get i18n() {
            return i18n();
          },
          dispatch_blob,
          get waveform_settings() {
            return waveform_settings();
          },
          get waveform_options() {
            return waveform_options();
          },
          get trim_region_settings() {
            return trim_region_settings();
          },
          get handle_reset_value() {
            return handle_reset_value();
          },
          get editable() {
            return editable();
          },
          get loop() {
            return loop();
          },
          interactive: true,
          get mode() {
            return get(mode);
          },
          set mode($$value) {
            set(mode, $$value);
          },
          $$events: {
            stop($$arg) {
              bubble_event.call(this, $$props, $$arg);
            },
            play($$arg) {
              bubble_event.call(this, $$props, $$arg);
            },
            pause($$arg) {
              bubble_event.call(this, $$props, $$arg);
            },
            edit($$arg) {
              bubble_event.call(this, $$props, $$arg);
            }
          },
          $$legacy: true
        });
      }
      append($$anchor2, fragment_8);
    };
    if_block(node_2, ($$render) => {
      if (value() === null || streaming()) $$render(consequent_3);
      else $$render(alternate_2, false);
    });
  }
  var node_10 = sibling(node_2, 2);
  SelectSource(node_10, {
    get sources() {
      return sources();
    },
    handle_clear: clear,
    get active_source() {
      return active_source();
    },
    set active_source($$value) {
      active_source($$value);
    },
    $$legacy: true
  });
  reset(div);
  template_effect(() => set_class(div, 1, `audio-container ${class_name() ?? ""}`, "svelte-ocxd3m"));
  append($$anchor, fragment);
  pop();
}
export {
  InteractiveAudio as I
};
//# sourceMappingURL=D2gsMg7z.js.map
