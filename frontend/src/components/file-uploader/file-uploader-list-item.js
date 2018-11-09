import React from 'react';
import PropTypes from 'prop-types';
import { gettext } from '../../utils/constants';

const propTypes = {
  item: PropTypes.object.isRequired,
  onUploaderCancel: PropTypes.func.isRequired,
};

class FileUploaderListItem extends React.Component {

  onUploaderCancel = () => {
    let item = this.props.item;
    item.resumableFile.cancel();
    this.props.onUploaderCancel(item);
  }

  formatFileSize = (size) => {
    if (typeof size !== 'number') {
      return '';
    }
    if (size >= 1000 * 1000 * 1000) {
      return (size / (1000 * 1000 * 1000)).toFixed(1) + ' G';
    }
    if (size >= 1024 * 1024) {
      return (size / (1000 * 1000)).toFixed(1) + ' M';
    }
    if (size >= 1000) {
      return (size / 1000).toFixed(1) + ' K';
    }
    return size.toFixed(1) + ' B';
  }

  render() {
    let { item } = this.props;
    return (
      <tr className="file-upload-item">
        <td width="50%" className="upload-name ellipsis">{item.resumableFile.relativePath}</td>
        <td width="30%" className="upload-progress upload-size">
          {
            item.progress === 100 ? this.formatFileSize(item.resumableFile.size) : item.progress + '%'
          }
        </td>
        <td width="20%" className="upload-operation">
          { this.props.item.progress !== 100 ?
            <span className="a-simulate" onClick={this.onUploaderCancel}>{gettext(('cancel'))}</span> :
            <span>{gettext('uploaded')}</span>
          }
        </td>
      </tr>
    );
  }
}

FileUploaderListItem.propTypes = propTypes;

export default FileUploaderListItem;