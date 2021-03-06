# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Utilties for V2 control flow."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensorflow.python.eager import context
from tensorflow.python.eager import function
from tensorflow.python.framework import ops
from tensorflow.python.framework.func_graph import FuncGraph


class CondBranchFuncGraph(FuncGraph):
  """FuncGraph for branches of tf.cond().

  This is used to distinguish cond branches from other functions.
  """
  pass


class WhileCondFuncGraph(FuncGraph):
  """FuncGraph for the condition of tf.while_loop().

  This is used to distinguish while conditions from other functions.
  """
  pass


class WhileBodyFuncGraph(FuncGraph):
  """FuncGraph for the body of tf.while_loop().

  This is used to distinguish while bodies from other functions.
  """
  pass


def in_defun():
  """Returns if the current graph is, or is nested in, a defun."""
  if context.executing_eagerly(): return False

  graph = ops.get_default_graph()
  while (isinstance(graph, CondBranchFuncGraph) or
         isinstance(graph, WhileBodyFuncGraph)):
    graph = graph.outer_graph
  return isinstance(graph, FuncGraph)


def create_new_tf_function(func_graph):
  """Converts func_graph to a TF_Function and adds it to the current graph.

  Args:
    func_graph: FuncGraph

  Returns:
    The name of the new TF_Function.
  """
  func = function._EagerDefinedFunction(  # pylint: disable=protected-access
      func_graph.name, func_graph, func_graph.inputs, func_graph.outputs, {})
  func.add_to_graph(func_graph.outer_graph)
  return func_graph.name


def unique_fn_name(scope, name):
  """Returns a unique name to use for a control flow function.

  Args:
    scope: A name scope string.
    name: An identifier for this function (e.g. "true", "body").

  Returns:
    A string, the name to use for the function.
  """
  return ("%s%s_%s" % (scope, name, ops.uid())).replace("/", "_")


def unique_grad_fn_name(forward_name):
  return "%s_grad_%s" % (forward_name, ops.uid())
