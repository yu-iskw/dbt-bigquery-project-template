
{% macro already_exists() %}
    {#--
       The macro was implemented with dbt 0.18.1.
       If dbt will change the specification of 'adapter', we have to improve the macro.
    #}
    {% if not execute %}
        {{ return(False) }}
    {% else %}
        {% set relation = adapter.get_relation(this.database, this.schema, this.table) %}
        {{ return(relation is not none
                  and relation.type == 'table') }}
    {% endif %}
{% endmacro %}
