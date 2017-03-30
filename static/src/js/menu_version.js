(function() {
    'use strict';
    var _t = openerp._t;
    
    var website=openerp.website;
    var QWeb = openerp.qweb;
    website.add_template_file('/website_version/static/src/xml/version_templates.xml');
    
    website.EditorVersion = openerp.Widget.extend({
        start: function() {
            var self = this;

            $('html').data('version_id', this.$el.find("#version-menu-button").data("version_id"));
            var _get_context = website.get_context;
            website.get_context = function (dict) {
                return _.extend({ 'version_id': $('html').data('version_id') }, _get_context(dict));
            };

            self.$el.on('click', 'a[data-action]', function(ev) {
                ev.preventDefault();
                self[$(this).data('action')](ev);
            });

            this.$el.find('#version-menu-button').click(function() {
                var view_id = parseInt($('html').attr('data-view-xmlid'));
                openerp.jsonRpc( '/website_version/all_versions', 'call', {'view_id': view_id}).then(function (result) {
                    self.$el.find(".o_version_choice").remove();
                    self.$el.find(".first_divider").before(QWeb.render("all_versions", {versions:result}));
                });;
                
            });
            return this._super();
        },
        
        duplicate_version: function(event) {
            var version_id = $('html').data('version_id');
            var wizardA = $(openerp.qweb.render("website_version.new_version",{'default_name': moment().format('l k:m')}));
            wizardA.appendTo($('body')).modal({"keyboard" :true});
            wizardA.on('click','.o_create', function(){
                wizardA.find('.o_message').remove();
                var version_name = wizardA.find('.o_version_name').val();
                if(version_name.length == 0){
                    wizardA.find(".o_version_name").after("<p class='o_message' style='color : red'> *"+_t("This field is required")+"</p>");
                }
                else{
                    wizardA.modal("hide");
                    openerp.jsonRpc( '/website_version/create_version', 'call', { 'name': version_name, 'version_id': version_id}).then(function (result) {

                        var wizard = $(openerp.qweb.render("website_version.dialogue",{message:_.str.sprintf("You are now working on version: %s.", version_name),
                                                                                       dialogue:_.str.sprintf("If you edit this page or others, all changes will be recorded in the version. It will not be visible by visitors until you publish the version.")}));
                        wizard.appendTo($('body')).modal({"keyboard" :true});
                        wizard.on('click','.o_confirm', function(){
                            window.location.href = '';
                        });
                        wizard.on('hidden.bs.modal', function () {$(this).remove();});
                    }).fail(function(){
                        var wizard = $(openerp.qweb.render("website_version.message",{message:_t("This name already exists.")}));
                        wizard.appendTo($('body')).modal({"keyboard" :true});
                        wizard.on('hidden.bs.modal', function () {$(this).remove();});
                    });
                }
            });
            wizardA.on('hidden.bs.modal', function () {$(this).remove();});
        },
        
        change_version: function(event) {
            var version_id = parseInt($(event.target).parent().data("version_id"));
            if(! version_id){
                version_id = 0;//By default master
            }
            openerp.jsonRpc( '/website_version/change_version', 'call', { 'version_id':version_id }).then(function (result) {
                    location.reload();
                });
        },

        delete_version: function(event) {
            console.log(event);
            var version_id = parseInt($(event.currentTarget).parent().data("version_id"));
            var name = $(event.currentTarget).parent().children(':last-child').text();
            var wizardA = $(openerp.qweb.render("website_version.delete_message",{message:_.str.sprintf("Are you sure you want to delete the %s version ?", name)}));
            wizardA.appendTo($('body')).modal({"keyboard" :true});
            wizardA.on('click','.o_confirm', function(){
                openerp.jsonRpc( '/website_version/delete_version', 'call', { 'version_id':version_id }).then(function (result) {
                    var wizardB = $(openerp.qweb.render("website_version.message",{message:_.str.sprintf("The %s version has been deleted.", result)}));
                    wizardB.appendTo($('body')).modal({"keyboard" :true});
                    wizardB.on('click','.o_confirm', function(){
                        location.reload();
                    wizardB.on('hidden.bs.modal', function () {$(this).remove();});
                    });
                });
            });
            wizardA.on('hidden.bs.modal', function () {$(this).remove();});

        },

        publish_version: function(event) {
            var version_id = parseInt($('html').data('version_id'));
            var name = $('#version-menu-button').attr('data-version_name');
            openerp.jsonRpc( '/website_version/diff_version', 'call', { 'version_id':version_id}).then(function (result) {
                console.log(result);
                var wizardA = $(openerp.qweb.render("website_version.publish_message",{message:_.str.sprintf("Publish Version %s", name), list:result}));
                wizardA.appendTo($('body')).modal({"keyboard" :true});
                wizardA.on('click','.o_confirm', function(){
                    wizardA.find('.o_message').remove();
                    var check = wizardA.find('.o_check').is(':checked');
                    var copy_master_name = wizardA.find('.o_name').val();
                    if(check){
                        if(copy_master_name.length == 0){
                            wizardA.find(".o_name").after("<p class='o_message' style='color : red'> *"+_t("This field is required")+"</p>");
                        }
                        else{
                            openerp.jsonRpc( '/website_version/publish_version', 'call', { 'version_id':version_id, 'save_master':true, 'copy_master_name':copy_master_name}).then(function (result) {
                                var wizardB = $(openerp.qweb.render("website_version.dialogue",{message:_.str.sprintf("The %s version has been published", result), dialogue:_.str.sprintf("The master has been saved on a new version called %s.",copy_master_name)}));
                                wizardB.appendTo($('body')).modal({"keyboard" :true});
                                wizardB.on('click','.o_confirm', function(){
                                    location.reload();
                                });
                                wizardB.on('hidden.bs.modal', function () {$(this).remove();});
                            });
                        }
                    }
                    else{
                        openerp.jsonRpc( '/website_version/publish_version', 'call', { 'version_id':version_id, 'save_master':false, 'copy_master_name':""}).then(function (result) {
                            var wizardC = $(openerp.qweb.render("website_version.message",{message:_.str.sprintf("The %s version has been published.", result)}));
                            wizardC.appendTo($('body')).modal({"keyboard" :true});
                            wizardC.on('click','.o_confirm', function(){
                                location.reload();
                            });
                            wizardC.on('hidden.bs.modal', function () {$(this).remove();});
                        });
                    }
                });
                wizardA.on('click','input[name="optionsRadios"]', function(){
                    wizardA.find('.o_message').remove();
                    wizardA.find('.o_name').toggle( wizardA.find('.o_check').is(':checked') );
                });
                wizardA.on('hidden.bs.modal', function () {$(this).remove();});
            });
        },

        diff_version: function(event) {
            var version_id = parseInt($('html').data('version_id'));
            var name = $('#version-menu-button').data('version_name');
            openerp.jsonRpc( '/website_version/diff_version', 'call', { 'version_id':version_id}).then(function (result) {
                var wizard = $(openerp.qweb.render("website_version.diff",{list:result, version_name:name}));
                wizard.appendTo($('body')).modal({"keyboard" :true});
                wizard.on('click','.o_confirm', function(){});
                wizard.on('hidden.bs.modal', function () {$(this).remove();});
            });
        }
    });

    $(document).ready(function() {
        var version = new website.EditorVersion();
        version.setElement($("#version-menu"));
        version.start();
    });
    
})();
