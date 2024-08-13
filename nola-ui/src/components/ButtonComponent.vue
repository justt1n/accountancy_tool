<template>
    <button
      :class="computedClass"
      :type="type"
      @click="handleClick"
    >
      <slot></slot>
    </button>
  </template>
  
  <script>
  export default {
    name: 'ButtonComponent',
    props: {
      type: {
        type: String,
        default: 'button',
      },
      variant: {
        type: String,
        default: 'primary',
      },
      disabled: {
        type: Boolean,
        default: false,
      },
    },
    computed: {
      computedClass() {
        const baseClass = 'btn';
        const variantClass = this.variant ? `btn-${this.variant}` : '';
        const disabledClass = this.disabled ? 'btn-disabled' : '';
        return `${baseClass} ${variantClass} ${disabledClass}`;
      },
    },
    methods: {
      handleClick(event) {
        if (!this.disabled) {
          this.$emit('click', event);
        }
      },
    },
  };
  </script>
  
  <style>

  </style>