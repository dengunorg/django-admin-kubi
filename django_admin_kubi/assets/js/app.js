var app = {
  init: function () {
    const _self = this;
    $(document).ready(function(){
      if ($('.change-list .btn-toolbar').length > 0) {
        setTimeout(function() {
          $('.search-spacer').width($('.change-list .btn-toolbar').outerWidth());
        }, 123);
      }
    })

    $('.fieldset-fields.collapse').each(function(i, el){
      if($(el).find(".has-error").length > 0) {
        $(el).addClass("show");
        $(el).parent().find(".fieldset-toggle").removeClass("collapsed");
      }
    })

    $('[data-bs-toggle="sidebar"]').on('click', function onSidebarClick() {
      $('body').toggleClass('open-sidebar');
    });

    $(".search-container").find('button[type="submit"]').on('click', function onSearchClick(e) {
      if ($("#search-input").val().length == 0) {
        e.preventDefault();
        $("#search-input").focus();
      }
    })

    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

    const toastTriggerList = document.querySelectorAll('[data-bs-toggle="toast"]')
    const toastList = [...toastTriggerList].map(toastTriggerEl => (
      new bootstrap.Toast(toastTriggerEl).show()
    ))
  },
  scrollTop: function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
};

(() => {
  'use strict'

  app.init();

})()