/*
    会话页进阶功能相关js方法
*/


// 安装卸载服务方法
function serviceFunc(sessid, type_str){
    $('#loader').html('<div class="spinner-border spinner-border-sm text-muted" role="status"></div>');
    $('.btn').addClass('disabled');
    let type_info = '安装';
    if (type_str === 'uninstall'){
        type_info = '卸载';
    }
    let name = $('#service-sub').val();
    let input_data = {
        'name': name,
        'type_str': type_str,
        'sessid': sessid
    }
    $.ajax({
        type: "POST",
        url: "/supershell/session/advanced/service",
        contentType: 'application/json',
        data: JSON.stringify(input_data),
        success: function(res) {
            if (res.stat === 'success'){
                $('#service-sub').val('');
                toastr.success(res.result, type_info + '服务成功: ' + name);
            }
            else if (res.stat === 'failed'){
                toastr.error(res.result, type_info + '服务失败: ' + name);
            }
            $('.btn').removeClass('disabled');
            $('#loader').html('<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-check" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">\
                <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>\
                <path d="M5 12l5 5l10 -10"></path>\
            </svg>');
        },
        error: function(data, type, error) {
            console.log(error);
            toastr.error(error.name + ": " + error.message,  type_info + '服务失败:' + name);
            $('.btn').removeClass('disabled');
            $('#loader').html('<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-check" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">\
                <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>\
                <path d="M5 12l5 5l10 -10"></path>\
            </svg>');
        },
    });
}


// 尝试更改uid、gid方法
function set_ugid(sessid, type_str){
    $('#loader').html('<div class="spinner-border spinner-border-sm text-muted" role="status"></div>');
    $('.btn').addClass('disabled');
    let type_info = '尝试设置uid';
    if (type_str === 'gid'){
        type_info = '尝试设置gid';
    }
    let id_num = $('#' + type_str + '-sub').val();
    let input_data = {
        'id_num': id_num,
        'type_str': type_str,
        'sessid': sessid
    }
    $.ajax({
        type: "POST",
        url: "/supershell/session/advanced/ugid",
        contentType: 'application/json',
        data: JSON.stringify(input_data),
        success: function(res) {
            if (res.stat === 'success'){
                $('#' + type_str + '-sub').val('');
                toastr.success(res.result, type_info + '成功: ' + id_num);
            }
            else if (res.stat === 'failed'){
                toastr.error(res.result, type_info + '失败: ' + id_num);
            }
            $('.btn').removeClass('disabled');
            $('#loader').html('<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-check" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">\
                <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>\
                <path d="M5 12l5 5l10 -10"></path>\
            </svg>');
        },
        error: function(data, type, error) {
            console.log(error);
            toastr.error(error.name + ": " + error.message,  type_info + '失败: ' + id_num);
            $('.btn').removeClass('disabled');
            $('#loader').html('<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-check" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">\
                <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>\
                <path d="M5 12l5 5l10 -10"></path>\
            </svg>');
        },
    });
}


// 开启关闭代理监听方法
function listenFunc(sessid, type_str){
    $('#loader').html('<div class="spinner-border spinner-border-sm text-muted" role="status"></div>');
    $('.btn').addClass('disabled');
    let type_info = '开启';
    if (type_str === 'off'){
        type_info = '关闭';
    }
    let address_proxy = $('#address-proxy').val();
    let port_proxy = $('#port-proxy').val();
    let input_data = {
        'address_proxy': address_proxy,
        'port_proxy': port_proxy,
        'type_str': type_str,
        'sessid': sessid
    }
    $.ajax({
        type: "POST",
        url: "/supershell/session/advanced/listen",
        contentType: 'application/json',
        data: JSON.stringify(input_data),
        success: function(res) {
            if (res.stat === 'success' && res.result.indexOf('failed') === -1){
                $('#address-proxy').val('');
                $('#port-proxy').val('');
                toastr.success(res.result, type_info + '代理监听成功: ' + address_proxy + ':' + port_proxy);
            }
            else{
                toastr.error(res.result, type_info + '代理监听失败: ' + address_proxy + ':' + port_proxy);
            }
            $('.btn').removeClass('disabled');
            $('#loader').html('<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-check" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">\
                <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>\
                <path d="M5 12l5 5l10 -10"></path>\
            </svg>');
        },
        error: function(data, type, error) {
            console.log(error);
            toastr.error(error.name + ": " + error.message,  type_info + '代理监听失败: ' + address_proxy + ':' + port_proxy);
            $('.btn').removeClass('disabled');
            $('#loader').html('<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-check" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">\
                <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>\
                <path d="M5 12l5 5l10 -10"></path>\
            </svg>');
        },
    });
}


// 查看已开启的代理监听方法
function showListenedFunc(sessid){
    $('#loader').html('<div class="spinner-border spinner-border-sm text-muted" role="status"></div>');
    $('.btn').addClass('disabled');
    let input_data = {
        'sessid': sessid
    }
    $.ajax({
        type: "POST",
        url: "/supershell/session/advanced/listen/show",
        contentType: 'application/json',
        data: JSON.stringify(input_data),
        success: function(res) {
            $('#listened-text').val(res.result);
            $('.btn').removeClass('disabled');
            $('#loader').html('<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-check" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">\
                <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>\
                <path d="M5 12l5 5l10 -10"></path>\
            </svg>');
        },
        error: function(data, type, error) {
            console.log(error);
            $('#listened-text').val(error.name + ": " + error.message);
            $('.btn').removeClass('disabled');
            $('#loader').html('<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-check" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">\
                <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>\
                <path d="M5 12l5 5l10 -10"></path>\
            </svg>');
        },
    });
}