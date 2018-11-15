from flask import jsonify, request
from . import api
from app.models import *
from flask_login import current_user
from ..util.utils import *


@api.route('/caseSet/add', methods=['POST'])
def add_set():
    data = request.json
    project_name = data.get('projectName')
    name = data.get('name')
    ids = data.get('id')
    project_id = Project.query.filter_by(name=project_name).first().id

    num = auto_num(data.get('num'), CaseSet, project_id=project_id)

    if ids:
        old_model_data = CaseSet.query.filter_by(id=ids).first()
        old_model_data.project_id = project_id
        old_model_data.name = name
        db.session.commit()
        return jsonify({'msg': '修改成功', 'status': 1})
    else:
        # if Module.query.filter_by(name=gather_name, project_id=project_id).first():
        #     return jsonify({'msg': '模块名字重复', 'status': 0})
        # else:
        new_set = CaseSet(name=name, project_id=project_id, num=num)
        db.session.add(new_set)
        db.session.commit()
        return jsonify({'msg': '新建成功', 'status': 1})


@api.route('/caseSet/stick', methods=['POST'])
def stick_set():
    data = request.json
    set_id = data.get('id')
    project_name = data.get('projectName')
    project_id = Project.query.filter_by(name=project_name).first().id
    _data = CaseSet.query.filter_by(id=set_id).first()
    num_sort('1', _data.num, CaseSet, project_id=project_id)
    db.session.commit()

    return jsonify({'msg': '置顶完成', 'status': 1})


@api.route('/caseSet/find', methods=['POST'])
def find_set():
    data = request.json
    page = data.get('page') if data.get('page') else 1
    per_page = data.get('sizePage') if data.get('sizePage') else 10
    project_name = data.get('projectName')
    if not project_name:
        return jsonify({'msg': '请先创建属于自己的项目', 'status': 0})

    pro_id = Project.query.filter_by(name=project_name).first().id
    # sets = CaseSet.query.filter_by(project_id=pro_id).order_by(CaseSet.num.asc()).all()
    # sets = [{'label': s.name, 'id': s.id, 'num': s.num} for s in sets]
    _set = CaseSet.query.filter_by(project_id=pro_id)
    pagination = _set.order_by(CaseSet.num.asc()).paginate(page, per_page=per_page, error_out=False)
    _items = pagination.items
    total = pagination.total
    current_set = [{'label': s.name, 'id': s.id} for s in _items]
    all_set = [{'label': s.name, 'id': s.id} for s in _set.all()]
    return jsonify({'status': 1, 'total': total, 'data': current_set, 'all_set': all_set})


@api.route('/caseSet/edit', methods=['POST'])
def edit_set():
    data = request.json
    set_id = data.get('id')
    _edit = CaseSet.query.filter_by(id=set_id).first()
    _data = {'name': _edit.name, 'num': _edit.num}

    return jsonify({'data': _data, 'status': 1})


@api.route('/caseSet/del', methods=['POST'])
def del_set():
    data = request.json
    set_id = data.get('id')
    _edit = CaseSet.query.filter_by(id=set_id).first()
    scene = Case.query.filter_by(case_set_id=set_id).first()
    if current_user.id != Project.query.filter_by(id=_edit.project_id).first().user_id:
        return jsonify({'msg': '不能删除别人项目下的模块', 'status': 0})
    if scene:
        return jsonify({'msg': '请先删除集合下的接口用例', 'status': 0})

    db.session.delete(_edit)
    return jsonify({'msg': '删除成功', 'status': 1})
