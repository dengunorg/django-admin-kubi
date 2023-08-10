!function ($, window) {
    "use strict";

    var jQuery = $;
    jQuery.expr[':'].parents = function(a, i, m) {
        return jQuery(a).parents(m[3]).length < 1;
    };

    jQuery(function($){
        var TranslationField = function (options) {
            this.el = options.el;
            this.cls = options.cls;
            this.id = '';
            this.origFieldname = '';
            this.lang = '';
            this.groupId = '';

            this.init = function () {
                var clsBits = this.cls.substring(
                    TranslationField.cssPrefix.length, this.cls.length).split('-');
                this.origFieldname = clsBits[0];
                this.lang = clsBits[1];
                this.id = $(this.el).attr('id');
                this.groupId = this.buildGroupId();
            };

            this.buildGroupId = function () {
                /**
                 * Returns a unique group identifier with respect to the admin's way
                 * of handling inline field name attributes. Essentially that's the
                 * translation field id without the language prefix.
                 *
                 * Examples ('id parameter': 'return value'):
                 *
                 *  'id_name_de':
                 *      'id_name'
                 *  'id_name_zh_tw':
                 *      'id_name'
                 *  'id_name_set-2-name_de':
                 *      'id_name_set-2-name'
                 *  'id_name_set-2-name_zh_tw':
                 *      'id_name_set-2-name'
                 *  'id_name_set-2-0-name_de':
                 *      'id_name_set-2-0-name'
                 *  'id_name_set-2-0-name_zh_tw':
                 *      'id_name_set-2-0-name'
                 *  'id_news-data2-content_type-object_id-0-name_de':
                 *      'id_news-data2-content_type-object_id-0-name'
                 *  'id_news-data2-content_type-object_id-0-name_zh_cn':
                 *      id_news-data2-content_type-object_id-0-name'
                 *  'id_news-data2-content_type-object_id-0-1-name_de':
                 *      'id_news-data2-content_type-object_id-0-1-name'
                 *  'id_news-data2-content_type-object_id-0-1-name_zh_cn':
                 *      id_news-data2-content_type-object_id-0-1-name'
                 */
                // TODO: We should be able to simplify this, the modeltranslation specific
                // field classes are already build to be easily splitable, so we could use them
                // to slice off the language code.
                var idBits = this.id.split('-'),
                    idPrefix = 'id_' + this.origFieldname;
                if (idBits.length === 3) {
                    // Handle standard inlines
                    idPrefix = idBits[0] + '-' + idBits[1] + '-' + idPrefix;
                } else if (idBits.length === 4) {
                    // Handle standard inlines with model used by inline more than once
                    idPrefix = idBits[0] + '-' + idBits[1] + '-' + idBits[2] + '-' + idPrefix;
                } else if (idBits.length === 6) {
                    // Handle generic inlines
                    idPrefix = idBits[0] + '-' + idBits[1] + '-' + idBits[2] + '-' +
                        idBits[3] + '-' + idBits[4] + '-' + this.origFieldname;
                } else if (idBits.length === 7) {
                    // Handle generic inlines with model used by inline more than once
                    idPrefix = idBits[0] + '-' + idBits[1] + '-' + idBits[2] + '-' +
                        idBits[3] + '-' + idBits[4] + '-' + idBits[5] + '-' + this.origFieldname;
                }
                return idPrefix;
            };

            this.init();
        };
        TranslationField.cssPrefix = 'mt-field-';

        var TranslationFieldGrouper = function (options) {
            this.$fields = options.$fields;
            this.groupedTranslations = {};

            this.init = function () {
                // Handle fields inside collapsed groups as added by zinnia
                this.$fields = this.$fields;

                this.groupedTranslations = this.getGroupedTranslations();
            };

            this.getGroupedTranslations = function () {
                /**
                 * Returns a grouped set of all model translation fields.
                 * The returned datastructure will look something like this:
                 *
                 * {
                 *     'id_name_de': {
                 *         'en': HTMLInputElement,
                 *         'de': HTMLInputElement,
                 *         'zh_tw': HTMLInputElement
                 *     },
                 *     'id_name_set-2-name': {
                 *         'en': HTMLTextAreaElement,
                 *         'de': HTMLTextAreaElement,
                 *         'zh_tw': HTMLTextAreaElement
                 *     },
                 *     'id_news-data2-content_type-object_id-0-name': {
                 *         'en': HTMLTextAreaElement,
                 *         'de': HTMLTextAreaElement,
                 *         'zh_tw': HTMLTextAreaElement
                 *     }
                 * }
                 *
                 * The keys are unique group identifiers as returned by
                 * TranslationField.buildGroupId() to handle inlines properly.
                 */

                var self = this,
                    cssPrefix = TranslationField.cssPrefix;

                this.$fields.each(function (idx, el) {
                    $.each($(el).attr('class').split(' '), function(idx, cls) {
                        if (cls.substring(0, cssPrefix.length) === cssPrefix) {
                            var tfield = new TranslationField({el: el, cls: cls});
                            if (!self.groupedTranslations[tfield.groupId]) {
                                self.groupedTranslations[tfield.groupId] = {};
                            }
                            self.groupedTranslations[tfield.groupId][tfield.lang] = el;
                        }
                    });
                });
                return this.groupedTranslations;
            };

            this.init();
        };

        function createTabs(groupedTranslations) {
            var tabs = [];
            $.each(groupedTranslations, function (groupId, lang) {
                var tabsContainer = $('<div class="translation-tabs"></div>'),
                    tabsList = $('<ul class="tabs-handler nav nav-tabs"></ul>'),
                    insertionPoint;
                tabsContainer.append(tabsList);
                $.each(lang, function (lang, el) {
                    var container = $(el).closest('.form-group'),
                        label = $('label', container),
                        fieldLabel = container.find('label'),
                        tabId = 'tab_' + $(el).attr('id'),
                        panel,
                        tab;

                    // add name to tabs container
                    var default_field_name = $(el).attr('name');
                    if(default_field_name!=undefined){
                        default_field_name = default_field_name.replace('_'+lang, '');
                        tabsContainer.addClass(default_field_name+'-tabs')
                    }

                    if (!insertionPoint) {
                        insertionPoint = {
                            'insert': container.prev().length ? 'after' :
                                container.next().length ? 'prepend' : 'append',
                            'el': container.prev().length ? container.prev() : container.parent()
                        };
                    }
                    container.find('script').remove();
                    panel = $('<div class="tabs-content" data-lang="'+lang+'" id="' + tabId + '"></div>').append(container);
                    tab = $('<li class="nav-item' + (label.hasClass('required') ? ' required' : '') +
                            '"><a href="#' + tabId + '" class="nav-link">' + lang.replace('_', '-') + '</a></li>');
                    tabsList.append(tab);
                    tabsContainer.append(panel);
                });
                insertionPoint.el[insertionPoint.insert](tabsContainer);

                /// CREATE TABS
                tabsContainer.find(".tabs-content").hide();
                tabsContainer.find(".tabs-handler li a").click(function(){
                    tabsContainer.find(".tabs-handler li a").removeClass("active");
                    $(this).addClass("active");
                    tabsContainer.find(".tabs-content").hide();
                    tabsContainer.find($(this).attr("href")).show();

                    return false;
                });
                tabsContainer.find(".tabs-handler li a").eq(0).click();

                tabs.push(tabsContainer);
            });
            return tabs;
        }


        var TabularInlineGroup = function (options) {
            this.id = options.id;
            this.$id = null;
            this.$table = null;
            this.translationColumns = [];
            // TODO: Make use of this to flag required tabs
            this.requiredColumns = [];

            this.init = function () {
                this.$id = $('#' + this.id);
                this.$table = $(this.$id).find('table');
            };

            this.getAllGroupedTranslations = function () {
                var grouper = new TranslationFieldGrouper({
                    $fields: this.$table.find('.mt').filter('input, textarea, select').filter(':parents(.empty-form)')
                });
                this.initTable();
                return grouper.groupedTranslations;
            };

            this.getGroupedTranslations = function ($fields) {
                var grouper = new TranslationFieldGrouper({
                    $fields: $fields
                });
                return grouper.groupedTranslations;
            };

            this.initTable = function () {
                var self = this;
                // The table header requires special treatment. In case an inline
                // is declared with extra=0, the translation fields are not visible.
                var thGrouper = new TranslationFieldGrouper({
                    $fields: this.$table.find('.mt').filter('input, textarea, select')
                });
                this.translationColumns = this.getTranslationColumns(thGrouper.groupedTranslations);

                // The markup of tabular inlines is kinda weird. There is an additional
                // leading td.original per row, so we have one td more than ths.
                this.$table.find('th').each(function (idx) {
                    // Hide table heads from which translation fields have been moved out.
                    if($.inArray(idx, self.translationColumns) !== -1) {
                        $(this).remove();
                    }

                    // Remove language and brackets from table header,
                    // they are displayed in the tab already.
                    if ($(this).html() && $.inArray(idx, self.translationColumns) === -1) {
                        $(this).html($(this).html().replace(/ \[.+\]/, '').replace(/ \(.+\)/, ''));
                    }
                });

                this.$table.find(".original").removeClass("hide");
            };

            this.getTranslationColumns = function (groupedTranslations) {
                var translationColumns = [];
                // Get table column indexes which have translation fields, but omit the first
                // one per group, because that's where we insert our tab container.
                $.each(groupedTranslations, function (groupId, lang) {
                    var i = 0;
                    $.each(lang, function (lang, el) {
                        var column = $(el).closest('td').prevAll().length;
                        if (i > 0 && $.inArray(column, translationColumns) === -1) {
                            translationColumns.push(column);
                        }
                        i += 1;
                    });
                });
                return translationColumns;
            };

            this.getRequiredColumns = function () {
                var requiredColumns = [];
                // Get table column indexes which have required fields, but omit the first
                // one per group, because that's where we insert our tab container.
                this.$table.find('th.required').each(function () {
                    requiredColumns.push($(this).index() + 1);
                });
                return requiredColumns;
            };

            this.init();
        };

        function createTabularTabs(groupedTranslations) {
            var tabs = [];

            $.each(groupedTranslations, function (groupId, lang) {
                var tabsContainer = $('<td class="translation-tabs"></td>'),
                    tabsList = $('<ul class="tabs-handler nav nav-tabs"></ul>'),
                    insertionPoint;
                tabsContainer.append(tabsList);

                $.each(lang, function (lang, el) {
                    var $container = $(el).closest('td'),
                        $panel,
                        $tab,
                        tabId = 'tab_' + $(el).attr('id');
                    if (!insertionPoint) {
                        insertionPoint = {
                            'insert': $container.prev().length ? 'after' :
                                $container.next().length ? 'prepend' : 'append',
                            'el': $container.prev().length ? $container.prev() : $container.parent()
                        };
                    }
                    $panel = $('<div class="tabs-content" data-lang="'+lang+'" id="' + tabId + '"></div>').append($container);

                    // Turn the moved tds into divs
                    var attrs = {};
                    $.each($container[0].attributes, function(idx, attr) {
                        attrs[attr.nodeName] = attr.nodeValue;
                    });
                    $container.replaceWith(function () {
                        return $('<div />', attrs).append($(this).contents());
                    });

                    // TODO: Setting the required state based on the default field is naive.
                    // The user might have tweaked his admin. We somehow have to keep track of the
                    // column indexes _before_ the tds have been moved around.
                    $tab = $('<li' + ($(el).hasClass('mt-default') ? ' class="required"' : '') +
                             '><a href="#' + tabId + '">' + lang.replace('_', '-') + '</a></li>');
                    tabsList.append($tab);
                    tabsContainer.append($panel);
                });
                insertionPoint.el[insertionPoint.insert](tabsContainer);

                /// CREATE TABS
                tabsContainer.find(".tabs-content").hide();
                tabsContainer.find(".tabs-handler li a").click(function(){
                    tabsContainer.find(".tabs-handler li").removeClass("active");
                    $(this).parent().addClass("active");
                    tabsContainer.find(".tabs-content").hide();
                    tabsContainer.find($(this).attr("href")).show();

                    var this_td = tabsContainer.closest("td");
                    var this_idx = tabsContainer.closest("tr").find("td").index(this_td);
                    var this_th = tabsContainer.parents("table").find("thead th").eq(this_idx);
                    var label = this_th.data("label").replace(/ \[.+\]/, '').replace(/ \(.+\)/, '');
                    this_th.html(label);
                    this_th.html(this_th.html() + " ["+$(this).text()+"]");
                    return false;
                });
                tabsContainer.find(".tabs-handler li a").eq(0).click();

                tabs.push(tabsContainer);
            });
            return tabs;
        }

        var MainSwitch = {
            languages: [],
            default_language: null,
            $dropdown: $('<div class="dropdown-menu" aria-labelledby="translationSwitch"></div>'),
            inited: false,
            init: function(groupedTranslations, tabs) {
                this.update(groupedTranslations, tabs);
            },
            build: function(groupedTranslations){
                if(jQuery.isEmptyObject(groupedTranslations)){return false;}
                if(this.inited && this.languages.length>0){return false;}

                var self = this;
                var default_language = this.default_language;
                $.each(groupedTranslations, function (id, languages) {
                    $.each(languages, function (lang, el) {
                        if ($.inArray(lang, self.languages) < 0) {
                            if($(el).hasClass("mt-default")){
                              default_language = lang.replace('_', '-');
                            };
                            self.languages.push(lang);
                        }
                    });
                });

                this.default_language = default_language;
                if(this.languages.length>0){
                    this.buildswitch();
                }
            },
            buildswitch: function(){
                var self = this;
                var trans = this.default_language;

                $.each(this.languages, function (idx, language) {
                    var lang_value = language.replace('_', '-');
                    self.$dropdown.append($('<a class="dropdown-item" href="#" tabindex="-1" data-label="'+ lang_value +'" data-lang="' + idx + '">'+ lang_value +'</a>'));
                });

                $('#language_trigger').each(function(i, el){
                    var $trigger = $(el);
                    var trans_label = $trigger.data('label');

                    var dropdown_container = $('\
                        <div class="dropdown dropup">\
                            <button class="btn btn-dark dropdown-toggle" type="button" id="translationSwitch" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">\
                                '+trans_label+' <span class="badge bg-primary">'+trans+'</span>\
                            </button>\
                        </div>');

                    dropdown_container.append(self.$dropdown);

                    $trigger.find('.handle').append(dropdown_container);
                });

                if (this.languages.length > 1) {
                    $('.language_trigger_container').removeClass("d-none");
                }
                this.inited = true;
            },
            update: function(groupedTranslations, tabs_func) {
                var self = this;
                this.build(groupedTranslations);
                var tabs = tabs_func(groupedTranslations);

                this.$dropdown.find("a").on('click', function(e){
                    e.preventDefault();
                    var val = $(this).data();
                    self.$dropdown.find("a").removeClass("active");
                    $(this).addClass("active");
                    self.$dropdown.parent().find(".badge").text(self.languages[val.lang]);
                    $.each(tabs, function (idx, tab) {
                        tab.find(".tabs-handler li a").eq(parseInt(val.lang, 10)).click();
                    });

                    $(window).trigger("language:change", val);
                });

                this.activateDefaultLanguage();
            },

            activateDefaultLanguage: function(){
                this.$dropdown.find('a[data-label="'+this.default_language+'"]').click();
            },
            activateLanguage: function(lang){
                if(lang!=null){
                    this.$dropdown.find("a").each(function(i, el){
                        var val = $(el).data();
                        if(val.label==lang){
                            $(el).click();
                        }
                    });
                }
            },
            activateTab: function(tabs) {
                return;
            }
        };

        var check_errors = function(){
            var hidden_errors = $("#content form .tabs-content").find(".has-error");
            var errors = {}
            hidden_errors.each(function(i, el){
                var data = $(el).parents(".tabs-content").data();
                if(data.lang!==undefined){
                    if(errors[data.lang]===undefined){
                        errors[data.lang] = new Array();
                    }
                    errors[data.lang].push(el);
                }
            });

            var lang_with_most_errors = null;
            var last_error_count = 0;
            $.each(errors, function(i, lang){
                if(lang.length>last_error_count){
                    last_error_count = lang.length;
                    lang_with_most_errors = i;
                }
            });

            MainSwitch.activateLanguage(lang_with_most_errors);
        };

        if ($('body').hasClass('change-form')) {

            var grouper = new TranslationFieldGrouper({
                $fields: $('.mt').filter(':input').filter(':parents(.tabular)').add('fieldset.collapsed .mt')
            });
            MainSwitch.init(grouper.groupedTranslations, createTabs);

            // Group fields in (existing) tabular inlines
            $('div.inline-group > div.tabular').each(function () {
                var tabularInlineGroup = new TabularInlineGroup({
                    'id': $(this).parent().attr('id')
                });
                MainSwitch.update(tabularInlineGroup.getAllGroupedTranslations(), createTabularTabs);
            });


            $('body').ajaxComplete(function() {
                var ajax_grouper = new TranslationFieldGrouper({
                    $fields: $('#composer_form_cover .mt').filter(':input')
                });
                createTabs(ajax_grouper.groupedTranslations);
            });


            $(document).ready(function() {
                // handle inline formset translations
                $(document).on('formset:added', function(e) {
                    var $row = $(e.target);
                    var inlineType = $row.parents('.inline-group').data('inline-type');

                    var grouper = new TranslationFieldGrouper({
                        $fields: $row.find(".mt").filter(':input')
                    });

                    // Update the main switch as it is not aware of the newly created tabs
                    if(inlineType==='stacked') {
                        MainSwitch.update(grouper.groupedTranslations, createTabs);
                    } else if (inlineType==='tabular') {
                        MainSwitch.update(grouper.groupedTranslations, createTabularTabs);
                    }
                    MainSwitch.activateDefaultLanguage();
                })

                // CHECK FOR ERRORS
                setTimeout(check_errors, 90);
            });


        }

    });
}(django.jQuery, window);