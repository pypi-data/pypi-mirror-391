window.SmartSelect = (function () {

    const events = { load: [] };

    function trigger(eventName, payload) {
        (events[eventName] || []).forEach(fn => fn(payload));
    }

    function init(scope = document) {
        scope.querySelectorAll("select[data-select]").forEach((select) => {

            const $select = $(select);
            // ✅ Antes de iniciar, destruir si ya estaba inicializado
            if ($select.data('select2')) {
                $select.select2('destroy');
            }

            const type   = select.dataset.select;
            const model  = select.dataset.model;
            const depend = select.dataset.depend;
            const depSelect = depend ? scope.querySelector(`[name="${depend}"]`) : null;
            const url    = "/select2-plus/api/";

            

            // Config base
            const baseConfig = {
                placeholder: "Seleccionar",
                width: "100%",
                minimumResultsForSearch: type === "simple" ? Infinity : 0,
                dropdownParent:  $(select).closest('.modal-content').length ? $(select).closest('.modal-content') : null
            };

            // ✅ Inicialización base
            $select.select2(baseConfig);

            // ✅ Ahora sí marcamos que fue inicializado
            select.dataset.smartSelectInit = "1";

            // Autofocus al abrir (search / source)
            if (type === "search" || type === "source") {
                $select.on("select2:open", () => {
                    setTimeout(() => {
                        const input = document.querySelector(".select2-container--open .select2-search__field");
                        if (input) input.focus();
                    }, 0);
                });
            }

            // Carga estática
            function loadStatic() {
                if (depend && (!depSelect || !depSelect.value)) {
                    $select.empty().val(null).trigger("change");
                    return;
                }

                const params = new URLSearchParams({ model });
                if (type === "search") params.set("term", "");
                if (depend && depSelect.value) params.set(`depend_${depend}`, depSelect.value);

                fetch(`${url}?${params}`)
                    .then(r => r.json())
                    .then(data => {
                        $select.empty();
                        data.results.forEach(opt => {
                            $select.append(new Option(opt.text, opt.id));
                        });
                        $select.val(null).trigger("change");
                        trigger("load", select);
                    });
            }

            // ✅ Búsqueda dinámica (source)
            
            if (type === "source") {
                // destruir otra vez si existiera
                if ($select.data('select2')) {
                    $select.select2('destroy');
                }

                $select.select2({
                    placeholder: "Buscar",
                    width: "100%",
                    ajax: {
                        url,
                        dataType: "json",
                        delay: 250,
                        data: params => {
                            if (depend && (!depSelect || !depSelect.value)) return null;
                            return {
                                model,
                                term: params.term || "",
                                ...(depend && depSelect.value && { [`depend_${depend}`]: depSelect.value })
                            };
                        },
                        processResults: data => ({ results: data.results }),
                        cache: true
                    },
                    minimumInputLength: 3,
                    dropdownParent:  $(select).closest('.modal-content').length ? $(select).closest('.modal-content') : null
                });
            }

            // Recarga cuando cambia el dependiente
            if (depend && depSelect) {
                $(depSelect).on("change", () => {
                    if (type === "source") {
                        $select.val(null).trigger("change");
                    } else {
                        loadStatic();
                    }
                });
            }

        });
    }

    function on(eventName, fn) {
        if (events[eventName]) events[eventName].push(fn);
    }

    return { init, on };

})();

// 🔥 Reinicializar al cargar DOM
document.addEventListener("DOMContentLoaded", () => SmartSelect.init());

// 🔥 Reinicializar cuando HTMX inserta contenido
//htmx.on("htmx:afterSwap", (e) => SmartSelect.init(e.target));
// No necesita verificar htmx, simplemente nunca se dispara si no está cargado
document.addEventListener('htmx:afterSwap', (e) => {
    if (e.target && e.target.closest('.modal-content')) {
        SmartSelect.init(e.target);
    }
});

// 🔥 Reinicializar al abrir modal
document.addEventListener('shown.bs.modal', e => SmartSelect.init(e.target));

// 🔥 Destruir al cerrar modal
document.addEventListener('hidden.bs.modal', function(e) {
    e.target.querySelectorAll('select[data-select]').forEach(sel => {
        const $sel = $(sel);
        if ($sel.data('select2')) $sel.select2('destroy');
        sel.removeAttribute("data-smart-select-init");
    });
});
