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

App.modal = function ($this, html, size) {
    let modal_size = size || $this.data('modal-size') || 'sm'
    let url = $this.data('href') || $this.attr('href');
    let title = $this.attr('title');
    let $modal = $('.modal');
    $modal.attr('class', 'active modal modal-' + modal_size)

    let $body = $modal.find('.modal-body')
    $body.html("<div class=\"loading loading-lg\"></div>")

    $modal.find('.modal-title').html(title)
    $(document).on('click', '.modal .btn-clear', function () {
        $modal.removeClass('active');
        $body.html('')
    })
    if (html) {
        $body.html(html)
        return
    }
    $.ajax({
        type: 'GET',
        url: url,
        context: $this,
        beforeSend: function () {
            $modal.addClass('active');
        },
        error: function (jqXHR, statusText, error) {
            $body.html(jqXHR.responseText)
        },
        success: function (result) {
            $body.html(result)
        }
    });
}

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
                // let data = JSON.parse(jqXHR.responseText)
                // App.tip(data['msg'], 5000);
                console.log(statusText)
                console.log(error)
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
        console.log(file)

        formData.append('file', file);
        if (file.size > 1024 * 1024 * 4) {
            App.tip('文件不能超过4M')
            return false;
        }

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
            window.location.reload();
            console.log(e);
        }, false);
        xhr.send(formData);
    });

    $(document).on('click', '.ajax-modal', function () {
        let $this = $(this);
        App.modal($this)
        return false;
    });

    $(document).on('keyup', '[name="wd"]', function (e) {
        if (e.keyCode === 13) {
            $('.btn-search').trigger('click')
        }
    })

    $(document).on('click', '.btn-search', function () {
        let $this = $(this);
        let wd = $('[name="wd"]').val();
        window.location.href = $this.data('href') + wd;
    });

    $(document).on('click', '.file-item.video', function () {
        let $this = $(this);
        App.modal($this, "<div id=\"dplayer\"></div>", 'lg')

        function paly() {
            return new DPlayer({
                container: document.getElementById('dplayer'),
                video: {
                    url: $this.data('url'),
                },
                autoplay: true
            });
        }

        if (typeof (DPlayer) === "undefined") {
            jQuery.getScript('https://cdn.jsdelivr.net/npm/dplayer@1.26.0/dist/DPlayer.min.js', function (data, status, jqxhr) {
                paly();
            });
        } else {
            paly();
        }
    })

    window.load_url = {};
    $(window).scroll(function () {
        let scrollTop = $(window).scrollTop();
        let scrollHeight = $(document).height();
        let windowHeight = $(window).height();
        if (scrollTop + windowHeight >= scrollHeight - 50) {
            let file_list = $('.file-list')
            let page_url = file_list.data('page')
            if (page_url && !window.load_url[page_url]) {
                window.load_url[page_url] = page_url
                $('.loading').removeClass('d-none')
                $.get(window.page_url, {'page': window.btoa(page_url)}, function (data) {
                    if (file_list.hasClass('table')) {
                        file_list.find('tbody').append(data['html'])
                    } else {
                        file_list.append(data['html'])
                    }
                    file_list.data('page', data['page_url'])
                    $('.loading').addClass('d-none')
                    if (file_list.justifiedGallery) {
                        $('.justified-gallery').justifiedGallery('norewind');
                    }
                });
            }
        }
    });
});