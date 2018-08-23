define([
    'jquery',
    'underscore',
    'backbone',
    'moment',
    'common'
], function($, _, Backbone, Moment, Common) {
    'use strict';

    var View = Backbone.View.extend({
        id: 'repo-details',
        className: 'details-panel',

        template:  _.template($('#repo-details-tmpl').html()),

        initialize: function(options) {
            var _this = this;

            this.parentView = options.parentView;
            $(document).on('keydown', function(e) {
                // ESCAPE key pressed
                if (e.which == 27) {
                    _this.hide();
                }
            });
        },

        events: {
            'click .js-close': 'close'
        },

        render: function() {
            this.$el.html(this.template(this.data));
        },

        update: function(part_data) {
            if (part_data.error) {
                this.$('#file-count').html('<span class="error">' + gettext("Error") + '</span>');
                this.$('#owner-chain').html('<span class="error">' + gettext("Error") + '</span>');
            } else {
                this.$('#file-count').html(part_data.file_count);

                var owner_chain, time, user, html;
                owner_chain = part_data.owner_chain;
                html = ''

                for (var i = 0, len = owner_chain.length; i < len; i++) {
                    time = Common.getRelativeTimeStr(Moment(owner_chain[i].time));
                    user = owner_chain[i].to_user_name;
                    html += '<li style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:2;"><span title="'+time+'">'+user+'</span></li>';
                }
                this.$('#owner-chain').html('<ul>' + html + '</ul>');
                this.$('#owner-chain').closest('tr').children().css('vertical-align','top')
            }
        },

        hide: function() {
            this.$el.hide();
        },

        close: function() {
            this.hide();
            return false;
        },

        show: function(options) {
            this.data = options;
            this.render();

            if (!$('#' + this.id).length) {
                this.parentView.$('.main-panel-main-with-side').append(this.$el);
                if (!this.$el.is(':visible')) {
                    this.$el.show();
                }
            } else {
                this.$el.show();
            }
        }

    });

    return View;
});
