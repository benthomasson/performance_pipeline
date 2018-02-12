
from gevent_pipeline.fsm import State, transitions


{% for state in states%}
class _{{state.label}}(State):

{%for name, transitions in state.functions%}
    @transitions({%for transition in transitions%}'{{transition.to_state}}'{%if not loop.last%},{%endif%}{%endfor%})
    def {{name}}(self, controller{%if name != 'start' and name != 'end'%}, message_type, message{%endif%}):
{%for transition in transitions%}
        controller.changeState({{transition.to_state}})
{%-endfor%}
{%endfor%}

{{state.label}} = _{{state.label}}()
{%endfor%}

