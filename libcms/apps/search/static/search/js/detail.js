'use strict';
(function (React, $) {
  window.Ruslan = window.Ruslan || {};


  var API = function (settings) {
    this.getHoldingsInfo = function (params) {
      var defer = $.Deferred();
      $.get(settings.urls.holdings, params).done(function (data) {
        defer.resolve(data);
      }).error(function (error) {
        console.error('Error while loading holdings info', defer);
        defer.reject(error);
      });
      return defer;
    };
  };

  var api = null;

  var HoldingsTable = React.createClass({
    componentWillMount: function () {
      console.log(this.props.holdings);
    },
    render: function () {
      return (
        <div>Экземпляры</div>
      );
    }
  });

  var HoldingsApp = React.createClass({
    componentDidMount: function () {
      var self = this;
      api.getHoldingsInfo({
        recordId: this.props.recordId
      }).done(function (data) {
        self.setState({
          loaded: true,
          holdings: data
        });
      }).fail(function (error) {
        console.error('Error while holdings load', error);
        self.setState({
          error: 'При загрузке сведений об экземплярах возникла ошибка'
        });
      });
    },
    getInitialState: function () {
      return {
        loaded: false,
        error: ''
      };
    },
    render: function () {
      if (this.state.error) {
        return (
          <div>{ this.state.error }</div>
        );
      }

      if (!this.state.loaded) {
        return (
          <div>Загрузка информации об экземплярах...</div>
        );
      }

      return (
        <div>
          <HoldingsTable holdings={this.state.holdings} />
        </div>
      );
    }
  });

  /**
   * @param settings
   *  element - app element
   *  recordId - record identifier
   *  urls:
   *    holdings - must return holdings data
   * @constructor
   */
  Ruslan.HoldingsInfo = function (settings) {
    api = new API({
      urls: settings.urls
    });
    React.render(<HoldingsApp recordId={settings.recordId}/>, settings.element);
  };

})(window.React, window.$);
