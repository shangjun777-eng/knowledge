(function () {
    function renderAll() {
        if (!window.WaveDrom) return;

        var skin = document.documentElement.dataset.scheme === "light" ? "default" : "dark";

        document.querySelectorAll(".wavedrom-render").forEach(function (el) {
            var srcEl = document.getElementById(el.dataset.source);
            if (!srcEl) return;

            var src;
            try {
                src = JSON.parse(srcEl.textContent);
            } catch (e) {
                console.error("WaveDrom JSON parse error", e);
                return;
            }

            src.config = Object.assign({}, src.config, { skin: skin });
            el.innerHTML = "";
            WaveDrom.RenderWaveForm(Number(el.dataset.index), src, "wavedrom-");
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", renderAll);
    } else {
        renderAll();
    }

    window.addEventListener("onColorSchemeChange", renderAll);
})();
