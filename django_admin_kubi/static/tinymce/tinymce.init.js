
tinymce.init({
  selector: 'textarea[data-editor="tinymce"]',
  branding: false,
  min_height: 290,
  menubar: false,
  content_css: 'kubi',
  plugins: [
    'autolink',
    'code',
    'link',
    'anchor',
    'lists',
    'media',
    'table',
    'image',
    'quickbars',
    'wordcount',
    'pagebreak',
    'nonbreaking',
  ],
  toolbar: 'undo redo | numlist bullist | alignleft aligncenter alignright | link anchor | image media hr | removeformat code',
  quickbars_insert_toolbar: false,
  quickbars_selection_toolbar: 'bold italic underline strikethrough | formatselect | fontsizeselect | forecolor | blockquote',
  contextmenu: 'undo redo | inserttable | cell row column deletetable',
  init_instance_callback : function(editor) {
    const storedTheme = localStorage.getItem('theme')
    const getPreferredTheme = () => {
      if (storedTheme) {
        return storedTheme
      }
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    editor.contentDocument.body.setAttribute('data-theme', getPreferredTheme());


    editor.on('init', function () {
      editor.getContainer().style.transition='border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out';
    });
    editor.on('focus', function () {
      editor.getContainer().classList.add("is-focus");
    });
    editor.on('blur', function () {
      editor.getContainer().classList.remove("is-focus");
    });
  }
});
