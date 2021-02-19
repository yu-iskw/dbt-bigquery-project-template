{% macro test_advanced_relationships(model, field, to, column_name, ignore_values) %}

with parent as (

    select
        {{ field }} as id
    from
        {{ to }}

),

child as (

    select
        {{ column_name }} as id
    from
        {{ model }}
    where
        {{ column_name }} not in (
            {{ ignore_values | join(', ') }}
        )
)

select count(*)
from child
where id is not null
  and id not in (select id from parent)

{% endmacro %}