# Other recording targets

Use the designated backend in the current environment; read its relevant skill
and current tool schema before interaction. Do not infer platform support from
the presence of a command named `record`.

| Target | Preferred route |
| --- | --- |
| iOS simulator / Android | Native device screen recording through the configured device backend. If Argent is configured, use its recording skill and start/stop tools. |
| Physical phone | Only the connected-device backend's supported recorder and permissions; do not assume simulator recording APIs exist. |
| Collaborative browser | The app-owned preview recording start/stop tools for the exact tab. |
| Other browser / Electron | Its configured continuous tab/CDP recorder, when supported. |
| TV | Verify backend support; device interaction support does not imply recording support. |

For animation diagnosis, disable static-frame trimming and interaction overlays
when the backend offers those options. Preserve raw timing and native resolution;
overlays can be useful for a separate instructional edit. For Argent, use
`trimStatic: false` and `showTouches: false` when the exposed schema supports
them. Keep an auto-stop cap, retrieve/finalize even if it expires, and retain
reported capture duration and warnings.

Start recording before the first action. Saved/replayable automation is a
separate artifact from the video; create a flow as well only when requested or
useful within the authorized task. Record again after a material source change;
earlier videos are evidence of their original state.

Do not fall back to browser screenshots or simulator screenshot polling for
motion review. If the backend lacks continuous recording, state the limitation
and prepare the native recording route rather than presenting an assembled
slideshow as a faithful video.
