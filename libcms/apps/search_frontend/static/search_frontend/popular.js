(function () {

  class ReactiveValue {
    #value = '';
    constructor(value) {
      this.#value = value;
    }
    set(value) {
      this.#value = value
    }
    get() {
      return this.#value;
    }
  }

  class Ref {
    el = undefined;
    set(el) {
      this.el = el;
    }
    get() {
      return this.el;
    }
  }

  function ref() {
    return new Ref();
  }

  class Node {
    #elementName = 'div';
    #classes = [];
    #events = {};
    #style = '';
    #ref = null;
    #text = '';
    #childrenNodes = [];

  }

  function node(elementName, {classes, events, style, ref, text}, childrenNodes = undefined) {
    const el = document.createElement(elementName);

    Object.entries(events).forEach(([name, cb]) => {
      el.addEventListener(name, cb);
    });

    const childrenEl = [];
    const removers = [];
    for (const [childEl, remover] of children) {
      childrenEl.push(childrenEl);
      removers.push(remover);
    }

    const remove = () => {
      Object.entries(events).forEach(([name, cb]) => {
        el.removeEvent(name, cb);
      });

      for (const remover of removers) {
        remover();
      }
      el.remove();
    }

    if (text !== undefined) {
      el.textContent = text.get();
    }

    if (ref !== undefined) {
      ref.set(el);
    }

    if (childrenNodes !== undefined) {
      for (const [nodeEl, nodeRemover] of childrenNodes) {
        el.appendChild(nodeEl);
        removers.push(nodeRemover);
      }
    }
    return [el, remove];
  }


  let nextId = 1;
  function nextComponentId() {
    nextId += 1;
    return String(nextId);
  }

  class Component {
    componentId = nextComponentId();
    #nodes = [];
    rendered = false;
    destroyed = false;
    destroy() {
      if (this.destroyed) {
        return;
      }
      for (const [el, remover] of this.#nodes) {
        remover();
      }
      this.destroyed = true;
    }
    markup() {
      return node('div')
    }
    render() {
      if (this.rendered) {
        return this.#nodes;
      }
      const nodes = this.markup();
      if (Array.isArray(nodes)) {
        this.#nodes = nodes;
      } else {
        this.#nodes = [nodes];
      }
      this.rendered = true;
      return this.#nodes;
    }
  }

  class Container extends Component{
    #components = [];
    add(component) {
      this.#components.push(component);
    }
    remove(componentId) {
      const componentIndex = this.#components.findIndex((component) => component.id = componentId);
      if (componentIndex > -1) {
        this.#components[componentIndex].destroy();
        this.#components.splice(componentIndex, 1);
      }
    }
    markup() {
      return this.#components.map((component) => component.render())
    }
  }

  function mount(toElement, component) {
    mountNode(toElement, component.render())
  }

  class Button extends Component {
    #config = {
      text: 'Кнопка',
    };
    #refs = {
      buttonEl: ref(),
    };
    #state = {
      text: new ReactiveValue(this.#config.text)
    }
    markup() {
      return (
        node('button',{
          classes: '',
          events: {
            onclick: () => this.handleClick()
          },
          text: this.#state.text,
          ref: this.#refs.buttonEl
        })
      )
    }
  }

  const buttons = new Container();
  buttons.add(new Button({
    text: '1235',
  }));
  buttons.add(new Button({
    text: '1235',
  }));
  buttons.add(new Button({
    text: '1235',
  }));



  function mountNode(toElement, node) {
    const removers = [];
    if (Array.isArray(node)) {
      for (const [el, remover] of node) {
        toElement.appendChild(el);
        removers.push(remover);
      }
    } else {
      const [el, remover] = node;
      toElement.appendChild(el)
      removers.push(remover);
    }
    return () => {
      for (const remover of removers) {
        remover();
      }
    }
  }


  function App() {

    return (
      node('div', {class: 'container'}, [
        node('div', {class: 'container__inner'}, [
          node('h2', {class: 'home-popular__title title'}),
          node('div', {class: 'home-popular__wrap'}, [
            node('div', {class: 'home-popular__info'}, [
              node('span', {class: 'home-popular__tag tag'}, 'Книги'),
              node('h2', {class: 'home-popular__info-title title title--middle'}, ''),
            ])
          ])
        ])
      ])
    )
  }

})();