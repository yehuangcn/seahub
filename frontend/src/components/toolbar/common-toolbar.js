import React from 'react';
import PropTypes from 'prop-types';
import { isPro, gettext } from '../../utils/constants';
import Search from '../search/search';
import Notification from '../common/notification';
import Account from '../common/account';

const propTypes = {
  onSearchedClick: PropTypes.func.isRequired,
  searchPlaceholder: PropTypes.string
};

class  CommonToolbar extends React.Component {
  render() {
    return (
      <div className="common-toolbar">
        {isPro && <Search onSearchedClick={this.props.onSearchedClick} placeholder={gettext(this.props.searchPlaceholder)}/>}
        <Notification  />
        <Account />
      </div>
    );
  }
}

CommonToolbar.propTypes = propTypes;

export default CommonToolbar;