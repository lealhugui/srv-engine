import traceback
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.conf import settings
import api.models as mdl
from meta import get_schema_instance

import logging
import json
logger = logging.getLogger('django')

# Create your views here.


def db_map_view(request):
    """returns the dbmap loaded on cache"""

    try:
        result = list()
        for scm in mdl.Schema.objects.all():
            r = model_to_dict(scm)

            r['tables'] = list()
            for tbl in scm.table_set.all():
                t_props = dict()
                data = list()
                if len(tbl.tablefield_set.all()) > 0:
                    data = [model_to_dict(tf) for tf in tbl.tablefield_set
                            .all().order_by('-is_primary_key')]
                t_props["fields"] = data
                t = model_to_dict(tbl)
                t["props"] = t_props
                r['tables'].append(t)
            result.append(r)
        return JsonResponse(result, safe=False)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'err': str(e),
            'errStack': traceback.format_exc()
        })


def table_info(request, name=None, get_table_size=False):
    """Return the metadata of the requested table"""

    try:
        if name is None:
            return JsonResponse({
                'success': False,
                'err': "Invalid table name"
            })

        t = mdl.Table.objects.filter(table_name=name)[0]

        if not t:
            return JsonResponse({'success': False, 'err': "Table not found"})

        t_props = dict()
        data = list()
        if len(t.tablefield_set.all()) > 0:
            data = [model_to_dict(tf) for tf in t.tablefield_set.all(
            ).order_by('-is_primary_key')]
        t_props["fields"] = data
        this_tbl = model_to_dict(t)
        this_tbl["props"] = t_props

        if get_table_size:
            schemas = getattr(settings, "META_DB_SCHEMAS", None)
            if not schemas:
                raise Exception('Schemas not configured')
            
            with get_schema_instance(schemas) as s:
                this_tbl["props"]["table_size"] = s.get_table_info(schemas[0], name).get_table_size(s)


        return JsonResponse(this_tbl, safe=False)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'err': str(e),
            'errStack': traceback.format_exc()
        })


def rebuild_db_map(request):
    """Collect the information of the observed database"""

    CACHE = None
    try:
        schemas = getattr(settings, "META_DB_SCHEMAS", None)
        if not schemas:
            raise Exception('Schemas not configured')
        with get_schema_instance(schemas) as s:
            CACHE = s.tables

        mdl.Schema.objects.all().delete()
        log_d = dict()
        for scm in schemas:
            s = mdl.Schema.objects.create(schema_name=scm)

            for tbl in [CACHE[t] for t in CACHE if CACHE[t].db_schema == scm]:
                # I don't bother saving table disk usage in the DB because it changes so
                # often that almost every query on it would be outdated. Insted, in the
                # "/table_info" endpoint there is a parameter to return it
                t = mdl.Table.objects.create(schema=s, table_name=tbl.name)
                for clm in tbl.columns:
                    mdl.TableField.objects.create(
                        table=t,
                        field_name=clm,
                        inner_type=tbl.columns[clm].column_type,
                        allow_null=tbl.columns[clm].allow_null,
                        is_primary_key=clm in tbl.pk
                    )

        with open('dump.json', 'w') as f:
            f.write(json.dumps(log_d, indent=4))

        return JsonResponse({'success': True})
    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'errTrace': traceback.format_exc(),
            'err': str(e)            
        })


def tables_with_pks(request):
    """Return a list of the tables with their respective PKs"""

    try:
        result = list()
        for scm in mdl.Schema.objects.all():
            for tbl in scm.table_set.all():
                t = {"Table Name": tbl.table_name}
                t["Primary Keys"] = ", ".join([
                    f.field_name
                    for f in
                    tbl.tablefield_set.filter(is_primary_key=True).all()
                ])

                result.append(t)
        return JsonResponse(result, safe=False)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'err': str(e),
            'errTrace': traceback.format_exc()
        })
