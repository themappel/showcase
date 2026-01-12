from main.signals import trends  # TODO: figure out a better way to do this other than imports
from main.signals import zoning
from main.signals import value
from main.signals import testing_signals
from main.signals import stoplimit
from main.signals import candles
import json
import main.api.helperBot as helperBot
import traceback
from main.constants import *


class Brain:
    def __init__(self):

        return

    """
    condition is a string which evaluates to some field that is present or not present in signal_info. If the field is not found 
    or the condition cannot be evaluated, this method returns false. 
    
    example condition: 
    signal_info["timestamp"]
    signal_info["trade_amount"] < 100
    signal_info==None
    not signal_info
    
    """

    def enter_flow(self, flow, signal_info):
        try:
            if eval(flow['start_condition']):
                helperBot.logv2(INFO, BRAIN,
                                {MSG: "flow start condition fulfilled", "condition": flow['start_condition'],
                                 "flow_id": flow['id']})
                return True
            else:
                helperBot.logv2(INFO, BRAIN,
                                {MSG: "flow start condition not fulfilled", "condition": flow['start_condition'],
                                 "flow_id": flow['id']})
                return False
        except Exception as e:
            helperBot.logv2(INFO, BRAIN,
                            {MSG: "flow start condition not fulfilled", "condition": flow['start_condition'],
                             "flow_id": flow['id'],
                             "stack_trace": traceback.format_exc(),
                             "exception": str(e)})
            return False

    """
    each flow contains steps, each step contains an action or actions, and a condition tree which if evaluated to true 
    will result in the execution of those actions. 
    
    
    Action can either be some function that is executed from here or a reference to a function that is then passed back to 
    the main minion flow 
    """

    def eval_flow(self, steps: list, df, ticker, signal_info):

        if signal_info is None:
            signal_info = {}

        action_list = []

        for step in steps:
            if self.eval_condition_tree(step['condition_tree'], df, ticker, signal_info):
                action_list.extend(step['actions'])

            helperBot.logv2(INFO, BRAIN,
                            {MSG: "Step evaluation Complete", "signal_info": signal_info,
                             "step_id": step['id'], "action_list": action_list})

        return action_list, signal_info

    def eval_condition_tree(self, condition_tree, df, ticker, signal_info):

        result = self.eval_layer(condition_tree, df, ticker, signal_info)

        helperBot.logv2(INFO, BRAIN,
                        {MSG: "Condition Tree Execution Complete", "signal_info": signal_info, "result": str(result),
                         "curr_candle": df[-1]})

        return result

    """
    first iteration of this recursive method to evaluate a decision tree. 
    1. work from the top down, if a link the chain evals to false, we can throw out the children paths 
    2. evaluate nodes in a layer that don't have children first, those are the quickest paths to a true result 
    
    
  
    """

    def eval_layer(self, layer: list, df, ticker, signal_info):

        # if nothing left in the layer return false
        if not layer:
            return False

        index = 0
        for condition in layer:

            # priotize conditions without children when iterating through tree
            if index == len(layer) - 1 or not condition['children']:
                try:
                    function_result = eval(
                        condition['function'] + "(df, ticker, signal_info, condition['options'])")
                except Exception as e:
                    helperBot.logv2(ERROR, BRAIN,
                                    {MSG: "Could not execute function: " + condition['function'],
                                     "stack_trace": traceback.format_exc(),
                                     "exception": str(e)})
                    function_result = False

                signal_info[condition['name']] = function_result

                if function_result:
                    if condition['children']:
                        if self.eval_layer(condition['children'], df, ticker, signal_info):
                            return True
                        else:
                            return self.eval_layer([x for x in layer if x != condition], df, ticker, signal_info)
                    else:
                        return True
                else:
                    return self.eval_layer([x for x in layer if x != condition], df, ticker, signal_info)
            index += 1

    def run_decisioning_v2(self, df, ticker, flows, signal_info=None):

        flow_processed = False
        action_list = None
        # go through the flows top down, first one meeting the condition we go down - if no conditions are met, throw an error
        for flow in flows:
            if self.enter_flow(flow, signal_info):
                flow_processed = True

                # we only want to execute one flow per decisioning run
                action_list, signal_info = self.eval_flow(flow['steps'], df, ticker, signal_info)
                helperBot.logv2(INFO, BRAIN,
                                {MSG: "Flow completed execution", "signal_info": signal_info,
                                 "flow_id": flow['id'], "action_list": action_list})

                if action_list:
                    break

        if not flow_processed:
            helperBot.logv2(WARN, BRAIN,
                            {MSG: "no flows executed",
                             "ticker": ticker,
                             "signal_info": signal_info})

        return action_list, signal_info

