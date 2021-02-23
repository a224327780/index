var App = App || {};

App.tip = function (message, time) {
    time = time || 4000;
    let body = $('body');
    let obj = body.find('.toast');
    if (!obj.length) {
        obj = $('<div/>', {'class': 'toast'});
        body.append(obj);
    }
    obj.html(message);
    window.setTimeout(function () {
        obj.remove();
    }, time);
};

$(function () {
    $(document).on('click', '.ajax', function () {
        let $this = $(this);
        let tr = $this.parents('tr')
        console.log(111);
        $.ajax({
            type: 'GET',
            url: $this.data('href'),
            dataType: 'json',
            context: $this,
            beforeSend: function () {
                tr.fadeOut()
            },
            error: function (jqXHR, statusText, error) {
                let data = JSON.parse(jqXHR.responseText)
                App.tip(data['msg'], 5000);
                tr.fadeIn()
            },
            success: function (result) {
                tr.remove();
            }
        });
    });

    $(document).on('click', '.submit', function () {
        let $this = $(this);
        let $form = $this.parents('form')
        $.ajax({
            type: 'POST',
            url: $form.attr('action'),
            data: $form.serialize(),
            dataType: 'json',
            context: $this,
            beforeSend: function () {
                $this.addClass('loading')
            },
            error: function (jqXHR, statusText, error) {
                let data = JSON.parse(jqXHR.responseText)
                App.tip(data['msg'], 5000);
                $this.removeClass('loading')
            },
            success: function (result) {
                window.location.reload();
            }
        });
    });

    $(document).on('click', '.upload-btn', function () {
        let $file = $('#btn_file');
        $file.click();
    });

    $(document).on('change', '#btn_file', function () {
        if (this.files.length <= 0) {
            return false;
        }
        let formData = new FormData();
        let file = this.files[0];
        formData.append('file', file);
        console.log(file)

        let xhr = new XMLHttpRequest();
        xhr.open("POST", $('.upload-btn').data('href'));
        let progress = $('.progress');
        progress.removeClass('d-none')
        xhr.upload.addEventListener('progress', function (e) {
            let percent = (e.loaded / e.total) * 100;
            console.log(e.loaded + '/' + e.total)
            progress.attr('value', percent)
        }, false);
        xhr.addEventListener('load', function (e) {
            App.tip('upload done.');
            progress.addClass('d-none');
            // window.location.reload();
            console.log(e);
        }, false);
        xhr.send(formData);
    });

    $(document).on('click', '.ajax-modal', function () {
        let $this = $(this);
        let url = $this.data('href') || $this.attr('href');
        $.get(url, function (html) {
            let $container = $("body").find('.modal-container')
            if (!$container.length) {
                $('body').append(html)
            } else {
                $container.html($(html).find('.modal-container').html())
            }
            let $modal = $('.modal');
            $modal.addClass('active');
            $container = $modal.find('.modal-container')
            $container.find('.btn-clear').on('click', function () {
                $modal.removeClass('active');
                $container.html('')
            });
        });
        return false;
    });

    window.load_url = {};
    $(window).scroll(function () {
        let scrollTop = $(window).scrollTop();
        let scrollHeight = $(document).height();
        let windowHeight = $(window).height();
        if (scrollTop + windowHeight >= scrollHeight - 50) {
            let table = $('.table')
            let page_url = table.data('page')
            if (page_url && !window.load_url[page_url]) {
                window.load_url[page_url] = page_url
                $('.loading').removeClass('d-none')
                $.get(window.page_url, {'page': window.btoa(page_url)}, function (data) {
                    table.find('tbody').append(data['html'])
                    table.data('page', data['page_url'])
                    $('.loading').addClass('d-none')
                });
            }
        }
    });
});